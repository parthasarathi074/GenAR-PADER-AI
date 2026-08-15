import json
import os
from pathlib import Path
from typing import Literal

import pandas as pd

from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field


# =============================================================================
# PATHS
# =============================================================================

CURRENT_FILE = Path(__file__).resolve()

APP_DIR = CURRENT_FILE.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

RELEASE_DATA_DIR = (
    PROJECT_ROOT
    / "release"
    / "data"
)

SOURCE_DATA_DIR = (
    PROJECT_ROOT
    / "data"
)

APP_DATA_DIR = (
    PROJECT_ROOT
    / "app_data"
)


def choose_data_dir() -> Path:
    """
    Select the validated application data source.

    Priority:
    1. Local validated release data
    2. Deployment-safe app_data package
    3. Development data directory
    """

    required_file = (
        "phase11_api_payload.json"
    )

    release_file = (
        RELEASE_DATA_DIR
        / required_file
    )

    app_file = (
        APP_DATA_DIR
        / required_file
    )

    source_file = (
        SOURCE_DATA_DIR
        / required_file
    )

    if release_file.exists():
        return RELEASE_DATA_DIR

    if app_file.exists():
        return APP_DATA_DIR

    if source_file.exists():
        return SOURCE_DATA_DIR

    raise RuntimeError(
        "Validated Phase 11 application outputs "
        "were not found."
    )


DATA_DIR = choose_data_dir()


# =============================================================================
# DATA FILES
# =============================================================================

DASHBOARD_FILE = (
    DATA_DIR
    / "phase11_dashboard_summary.json"
)

CANDIDATE_TABLE_FILE = (
    DATA_DIR
    / "phase11_candidate_table.csv"
)

CANDIDATE_CARDS_FILE = (
    DATA_DIR
    / "phase11_candidate_cards.json"
)

METADATA_FILE = (
    DATA_DIR
    / "phase11_application_metadata.json"
)

REPORT_FILE = (
    DATA_DIR
    / "phase10_pharmacovigilance_report.txt"
)


# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter(
    prefix="/api/assistant",
    tags=["GenAI Assistant"],
)


# =============================================================================
# REQUEST / RESPONSE MODELS
# =============================================================================

class ChatMessage(BaseModel):
    role: Literal[
        "user",
        "assistant",
    ]

    content: str = Field(
        min_length=1,
        max_length=6000,
    )


class AssistantRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=4000,
    )

    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=10,
    )


class AssistantResponse(BaseModel):
    answer: str

    model: str

    scope: str

    evidence_source: str

    safety: dict


# =============================================================================
# HELPERS
# =============================================================================

def load_json(path: Path):
    if not path.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                f"Required evidence file missing: "
                f"{path.name}"
            ),
        )

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to load "
                f"{path.name}: {exc}"
            ),
        )


def load_text(path: Path) -> str:
    if not path.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                f"Required report file missing: "
                f"{path.name}"
            ),
        )

    try:
        return path.read_text(
            encoding="utf-8"
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


def load_candidate_table():
    if not CANDIDATE_TABLE_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="Candidate table missing.",
        )

    try:
        dataframe = pd.read_csv(
            CANDIDATE_TABLE_FILE
        )

        dataframe = dataframe.where(
            pd.notnull(dataframe),
            None,
        )

        return dataframe.to_dict(
            orient="records"
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to read candidate table: "
                f"{exc}"
            ),
        )


# =============================================================================
# VALIDATED CONTEXT
# =============================================================================

def build_validated_context() -> str:
    dashboard = load_json(
        DASHBOARD_FILE
    )

    cards = load_json(
        CANDIDATE_CARDS_FILE
    )

    metadata = load_json(
        METADATA_FILE
    )

    candidates = load_candidate_table()

    report = load_text(
        REPORT_FILE
    )

    context = {
        "dashboard":
            dashboard,

        "candidate_table":
            candidates,

        "candidate_cards":
            cards,

        "application_metadata":
            metadata,

        "controlled_report":
            report,
    }

    return json.dumps(
        context,
        ensure_ascii=False,
        indent=2,
    )


# =============================================================================
# SYSTEM INSTRUCTIONS
# =============================================================================

SYSTEM_INSTRUCTIONS = """
You are the GenAR-PADER-AI pharmacovigilance
decision-support assistant.

You must answer ONLY from the VALIDATED PROJECT
EVIDENCE supplied to you.

The supplied evidence is the source of truth for
this conversation.

STRICT RULES

1. Do not introduce external medical facts,
   literature, guidelines, drug-label information,
   epidemiology, incidence estimates or general
   pharmacology unless they are explicitly present
   in the supplied project evidence.

2. If the evidence does not support the requested
   fact, clearly say:
   "The validated project evidence does not support
   that conclusion."

3. Reported case frequency is NOT incidence.

4. No internal non-Bisoprolol comparator exists.

5. ROR was NOT calculated.

6. PRR was NOT calculated.

7. Causality is NOT established.

8. Disproportionality is NOT established.

9. Candidate reactions are NOT confirmed safety
   signals.

10. Candidate reactions are NOT confirmed adverse
    reactions.

11. Co-medication patterns do NOT establish
    drug-drug interactions.

12. Review priority is a TRIAGE classification only.

13. Never convert "higher priority" into:
    - confirmed signal
    - stronger causality
    - increased risk
    - incidence
    - proven association

14. Never provide individual patient diagnosis,
    prescribing instructions, treatment advice,
    dose adjustment or medical emergency guidance
    from this dataset.

15. You may:
    - summarize candidate evidence
    - compare reported candidate counts
    - explain priority classifications
    - explain seriousness counts
    - summarize limitations
    - explain the analytical pipeline
    - explain why ROR/PRR are unavailable
    - identify the highest or lowest reported
      candidates
    - explain the validated dashboard fields

16. Keep numerical values exactly consistent with
    the supplied evidence.

17. When discussing a candidate, prefer the phrase:
    "reported cases"
    rather than:
    "patients affected"
    or
    "incidence".

18. If a user asks whether Bisoprolol caused a
    reaction, explicitly state that causality was
    not established by this project.

19. Keep answers concise and clear.

20. End analytical answers with a short scope note
    when appropriate:
    "This is descriptive/exploratory
    pharmacovigilance decision support."
"""


# =============================================================================
# OPENAI CLIENT
# =============================================================================

def get_client() -> OpenAI:
    if not os.getenv(
        "OPENAI_API_KEY"
    ):
        raise HTTPException(
            status_code=503,
            detail=(
                "OPENAI_API_KEY is not configured "
                "on the backend."
            ),
        )

    return OpenAI()


# =============================================================================
# STATUS ENDPOINT
# =============================================================================

@router.get("/status")
def assistant_status():
    return {
        "assistant":
            "GenAR-PADER-AI",

        "configured":
            bool(
                os.getenv(
                    "OPENAI_API_KEY"
                )
            ),

        "model":
            "gpt-5.6",

        "evidence_source":
            str(DATA_DIR),

        "scope":
            "validated_project_evidence_only",

        "web_search":
            False,

        "external_medical_sources":
            False,

        "causality_established":
            False,

        "disproportionality_established":
            False,
    }


# =============================================================================
# CHAT ENDPOINT
# =============================================================================

@router.post(
    "/chat",
    response_model=AssistantResponse,
)
def assistant_chat(
    request: AssistantRequest,
):
    question = (
        request.question
        .strip()
    )

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    client = get_client()

    validated_context = (
        build_validated_context()
    )

    history = request.history[-6:]

    conversation = []

    for message in history:
        conversation.append(
            {
                "role":
                    message.role,

                "content":
                    message.content,
            }
        )

    conversation.append(
        {
            "role":
                "user",

            "content":
                (
                    "VALIDATED PROJECT EVIDENCE\n"
                    "==========================\n"
                    f"{validated_context}\n\n"
                    "CURRENT USER QUESTION\n"
                    "=====================\n"
                    f"{question}"
                ),
        }
    )

    try:
        response = client.responses.create(
            model="gpt-5.6",

            instructions=(
                SYSTEM_INSTRUCTIONS
            ),

            input=conversation,

            store=False,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "OpenAI request failed: "
                f"{exc}"
            ),
        )

    answer = (
        response.output_text
        or ""
    ).strip()

    if not answer:
        raise HTTPException(
            status_code=502,
            detail=(
                "The model returned an empty response."
            ),
        )

    return AssistantResponse(
        answer=answer,

        model="gpt-5.6",

        scope=(
            "descriptive_exploratory_"
            "pharmacovigilance"
        ),

        evidence_source=(
            "validated_phase10_phase11_"
            "application_outputs"
        ),

        safety={
            "frequency_is_incidence":
                False,

            "causality_established":
                False,

            "disproportionality_established":
                False,

            "confirmed_signal":
                False,

            "confirmed_interaction":
                False,

            "ror_available":
                False,

            "prr_available":
                False,
        },
    )