import json
import os
from pathlib import Path
from typing import Literal

import pandas as pd

from fastapi import APIRouter, HTTPException
from groq import Groq
from pydantic import BaseModel, Field


# =============================================================================
# PATHS
# =============================================================================

CURRENT_FILE = Path(__file__).resolve()

APP_DIR = CURRENT_FILE.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

RELEASE_DATA_DIR = PROJECT_ROOT / "release" / "data"
SOURCE_DATA_DIR = PROJECT_ROOT / "data"
APP_DATA_DIR = PROJECT_ROOT / "app_data"


def choose_data_dir() -> Path:
    required_file = "phase11_api_payload.json"

    candidates = [
        RELEASE_DATA_DIR,
        APP_DATA_DIR,
        SOURCE_DATA_DIR,
    ]

    for directory in candidates:
        if (directory / required_file).exists():
            return directory

    raise RuntimeError(
        "Validated application evidence could not be located."
    )


DATA_DIR = choose_data_dir()


# =============================================================================
# FILES
# =============================================================================

DASHBOARD_FILE = (
    DATA_DIR / "phase11_dashboard_summary.json"
)

CANDIDATE_TABLE_FILE = (
    DATA_DIR / "phase11_candidate_table.csv"
)

METADATA_FILE = (
    DATA_DIR / "phase11_application_metadata.json"
)


# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter(
    prefix="/api/assistant",
    tags=["GenAI Assistant"],
)


# =============================================================================
# MODELS
# =============================================================================

class ChatMessage(BaseModel):
    role: Literal[
        "user",
        "assistant",
    ]

    content: str = Field(
        min_length=1,
        max_length=3000,
    )


class AssistantRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
    )

    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=6,
    )


class AssistantResponse(BaseModel):
    answer: str
    model: str
    provider: str
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
            detail=f"Missing evidence file: {path.name}",
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
            detail=f"Unable to read {path.name}: {exc}",
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
            detail=f"Unable to read candidate table: {exc}",
        )


# =============================================================================
# COMPACT VALIDATED CONTEXT
# =============================================================================

def build_validated_context() -> str:
    """
    Build a compact evidence payload suitable for
    Groq free-tier token limits.

    We intentionally exclude the large Phase 10
    human-readable report and candidate-card payload.
    """

    dashboard = load_json(
        DASHBOARD_FILE
    )

    metadata = load_json(
        METADATA_FILE
    )

    candidate_rows = load_candidate_table()

    compact_candidates = []

    for row in candidate_rows:
        compact_candidates.append(
            {
                "rank":
                    row.get("rank"),

                "reaction":
                    row.get("reaction"),

                "reported_cases":
                    row.get("reported_cases"),

                "percentage_of_all_cases":
                    row.get("percentage_of_all_cases"),

                "serious_cases":
                    row.get("serious_cases"),

                "serious_percentage":
                    row.get("serious_percentage"),

                "death_cases":
                    row.get("death_cases"),

                "hospitalization_cases":
                    row.get("hospitalization_cases"),

                "priority":
                    (
                        row.get("review_priority")
                        or row.get("priority")
                    ),
            }
        )

    compact_context = {
        "dataset": {
            "total_safety_reports":
                dashboard.get(
                    "total_safety_reports"
                ),

            "bisoprolol_cases":
                dashboard.get(
                    "bisoprolol_cases"
                ),

            "candidate_reactions":
                dashboard.get(
                    "candidate_reactions"
                ),

            "priority_distribution":
                dashboard.get(
                    "priority_distribution"
                ),

            "top_candidate":
                dashboard.get(
                    "top_candidate"
                ),
        },

        "candidates":
            compact_candidates,

        "analytical_status":
            dashboard.get(
                "analytical_status",
                {}
            ),

        "interpretation":
            dashboard.get(
                "interpretation"
            ),

        "priority_interpretation":
            dashboard.get(
                "priority_interpretation"
            ),

        "limitations":
            metadata.get(
                "limitations",
                []
            ),

        "analytical_restrictions":
            metadata.get(
                "analytical_restrictions",
                {}
            ),
    }

    return json.dumps(
        compact_context,
        ensure_ascii=False,
        separators=(",", ":"),
    )


# =============================================================================
# SYSTEM INSTRUCTIONS
# =============================================================================

SYSTEM_INSTRUCTIONS = """
You are the GenAR-PADER-AI pharmacovigilance evidence assistant.

Use ONLY the validated project evidence supplied in the current request.

Rules:

- Reported frequency is not incidence.
- No internal non-Bisoprolol comparator exists.
- ROR was not calculated.
- PRR was not calculated.
- Causality is not established.
- Disproportionality is not established.
- Candidate reactions are not confirmed safety signals.
- Review priority is a triage classification only.
- Co-medication patterns do not prove drug-drug interactions.
- Do not introduce external medical information.
- Do not provide diagnosis or treatment advice.
- Preserve all numerical values exactly.
- Prefer the phrase "reported cases".
- If evidence is insufficient, say:
  "The validated project evidence does not support that conclusion."
- Keep answers concise, usually under 150 words.
"""


# =============================================================================
# GROQ CLIENT
# =============================================================================

def get_client() -> Groq:
    api_key = os.getenv(
        "GROQ_API_KEY"
    )

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "The GenAI assistant is "
                "temporarily unavailable."
            ),
        )

    return Groq(
        api_key=api_key
    )


# =============================================================================
# STATUS
# =============================================================================

@router.get("/status")
def assistant_status():
    return {
        "assistant":
            "GenAR-PADER-AI",

        "configured":
            bool(
                os.getenv(
                    "GROQ_API_KEY"
                )
            ),

        "provider":
            "Groq",

        "model":
            "openai/gpt-oss-20b",

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
# CHAT
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

    messages = [
        {
            "role":
                "system",

            "content":
                SYSTEM_INSTRUCTIONS,
        }
    ]

    # Keep only a small recent history.
    for message in request.history[-4:]:
        messages.append(
            {
                "role":
                    message.role,

                "content":
                    message.content[:1500],
            }
        )

    messages.append(
        {
            "role":
                "user",

            "content":
                (
                    "VALIDATED PROJECT EVIDENCE:\n"
                    f"{validated_context}\n\n"
                    "QUESTION:\n"
                    f"{question}"
                ),
        }
    )

    try:
        response = (
            client
            .chat
            .completions
            .create(
                model="openai/gpt-oss-20b",

                messages=messages,

                temperature=0.1,

                max_completion_tokens=350,

                stream=False,
            )
        )

    except Exception as exc:
        print("\n" + "=" * 100)
        print("GROQ API ERROR")
        print("=" * 100)
        print(type(exc).__name__)
        print(str(exc))
        print("=" * 100 + "\n")

        raise HTTPException(
            status_code=503,
            detail=(
                "The GenAI assistant is temporarily "
                "unavailable. Please try again later."
            ),
        )

    answer = (
        response
        .choices[0]
        .message
        .content
        or ""
    ).strip()

    if not answer:
        raise HTTPException(
            status_code=503,
            detail=(
                "The GenAI assistant returned "
                "an empty response."
            ),
        )

    return AssistantResponse(
        answer=answer,

        model="openai/gpt-oss-20b",

        provider="Groq",

        scope=(
            "descriptive_exploratory_"
            "pharmacovigilance"
        ),

        evidence_source=(
            "validated_phase11_compact_context"
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