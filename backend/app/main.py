from pathlib import Path
from typing import Any

import json
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from backend.app.assistant import router as assistant_router


# =============================================================================
# PROJECT PATHS
# =============================================================================

CURRENT_FILE = Path(__file__).resolve()

BACKEND_DIR = CURRENT_FILE.parent.parent
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
    Select the application data source.

    Priority:
    1. Validated local release data
    2. Deployment-safe app_data package
    3. Development data directory

    The required Phase 11 API payload is used as the
    availability check.
    """

    required_file = "phase11_api_payload.json"

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
        "Could not locate Phase 11 application outputs. "
        "Expected phase11_api_payload.json in "
        "release/data, app_data, or data."
    )


DATA_DIR = choose_data_dir()


# =============================================================================
# APPLICATION DATA FILES
# =============================================================================

FILES = {
    "dashboard":
        DATA_DIR
        / "phase11_dashboard_summary.json",

    "candidate_table":
        DATA_DIR
        / "phase11_candidate_table.csv",

    "candidate_cards":
        DATA_DIR
        / "phase11_candidate_cards.json",

    "metadata":
        DATA_DIR
        / "phase11_application_metadata.json",

    "api_payload":
        DATA_DIR
        / "phase11_api_payload.json",

    "report":
        DATA_DIR
        / "phase10_pharmacovigilance_report.txt",

    "generated_report":
        DATA_DIR
        / "phase10_generated_report.json",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_json(
    path: Path,
) -> Any:
    """
    Safely load a JSON file.
    """

    if not path.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                f"Required data file missing: "
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
                f"Unable to read "
                f"{path.name}: "
                f"{str(exc)}"
            ),
        )


def load_candidate_table() -> pd.DataFrame:
    """
    Load the Phase 11 candidate table.
    """

    path = FILES[
        "candidate_table"
    ]

    if not path.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                "Candidate table is missing."
            ),
        )

    try:
        return pd.read_csv(
            path
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load candidate table: "
                f"{str(exc)}"
            ),
        )


def dataframe_records(
    dataframe: pd.DataFrame,
) -> list[dict]:
    """
    Convert a dataframe to JSON-safe records.
    """

    cleaned = dataframe.where(
        pd.notnull(
            dataframe
        ),
        None,
    )

    return cleaned.to_dict(
        orient="records"
    )


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="GenAR-PADER-AI API",

    description=(
        "Validated pharmacovigilance "
        "decision-support API."
    ),

    version="1.0.0",
)


# =============================================================================
# GENAI ASSISTANT ROUTER
# =============================================================================

app.include_router(
    assistant_router
)


# =============================================================================
# CORS
# =============================================================================

app.add_middleware(
    CORSMiddleware,

  allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://genar-pader-ai-14.vercel.app",
],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =============================================================================
# ROOT
# =============================================================================

@app.get("/")
def root():
    return {
        "project":
            "GenAR-PADER-AI",

        "version":
            "1.0.0",

        "status":
            "online",

        "pipeline_phases_completed":
            12,

        "data_source":
            str(DATA_DIR),

        "analysis_scope":
            "descriptive_exploratory_decision_support",

        "genai_assistant":
            "/api/assistant/status",
    }


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/health")
def health():
    file_status = {}

    all_available = True

    for name, path in FILES.items():
        exists = path.exists()

        file_status[
            name
        ] = exists

        if not exists:
            all_available = False

    return {
        "status":
            (
                "healthy"
                if all_available
                else "degraded"
            ),

        "data_source":
            str(DATA_DIR),

        "files":
            file_status,
    }


# =============================================================================
# DASHBOARD
# =============================================================================

@app.get(
    "/api/dashboard"
)
def dashboard():
    return load_json(
        FILES[
            "dashboard"
        ]
    )


# =============================================================================
# CANDIDATES
# =============================================================================

@app.get(
    "/api/candidates"
)
def candidates():
    dataframe = (
        load_candidate_table()
    )

    if "rank" in dataframe.columns:
        dataframe = (
            dataframe
            .sort_values(
                by="rank"
            )
        )

    return {
        "count":
            len(
                dataframe
            ),

        "candidates":
            dataframe_records(
                dataframe
            ),
    }


# =============================================================================
# SINGLE CANDIDATE BY RANK
# =============================================================================

@app.get(
    "/api/candidates/{rank}"
)
def candidate_by_rank(
    rank: int,
):
    dataframe = (
        load_candidate_table()
    )

    if "rank" not in dataframe.columns:
        raise HTTPException(
            status_code=500,
            detail=(
                "Candidate table does not contain "
                "a rank column."
            ),
        )

    matches = dataframe[
        dataframe[
            "rank"
        ]
        == rank
    ]

    if matches.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No candidate found "
                f"with rank {rank}."
            ),
        )

    table_record = (
        dataframe_records(
            matches
        )[0]
    )

    cards_data = load_json(
        FILES[
            "candidate_cards"
        ]
    )

    cards = []

    if isinstance(
        cards_data,
        dict,
    ):
        cards = (
            cards_data.get(
                "cards",
                []
            )
        )

    elif isinstance(
        cards_data,
        list,
    ):
        cards = cards_data

    card = next(
        (
            item
            for item in cards
            if int(
                item.get(
                    "rank",
                    -1,
                )
            )
            == rank
        ),
        None,
    )

    return {
        "table":
            table_record,

        "details":
            card,
    }


# =============================================================================
# CANDIDATE BY REACTION NAME
# =============================================================================

@app.get(
    "/api/reactions/{reaction_name}"
)
def candidate_by_reaction(
    reaction_name: str,
):
    dataframe = (
        load_candidate_table()
    )

    reaction_column = None

    if "reaction" in dataframe.columns:
        reaction_column = "reaction"

    elif "reactionmeddrapt" in dataframe.columns:
        reaction_column = (
            "reactionmeddrapt"
        )

    if reaction_column is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "Candidate table does not contain "
                "a reaction column."
            ),
        )

    normalized_query = (
        reaction_name
        .strip()
        .lower()
    )

    matches = dataframe[
        dataframe[
            reaction_column
        ]
        .astype(str)
        .str.strip()
        .str.lower()
        == normalized_query
    ]

    if matches.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                "Candidate reaction not found."
            ),
        )

    return dataframe_records(
        matches
    )[0]


# =============================================================================
# PRIORITY FILTER
# =============================================================================

@app.get(
    "/api/candidates/priority/{priority}"
)
def candidates_by_priority(
    priority: str,
):
    dataframe = (
        load_candidate_table()
    )

    priority_column = None

    if (
        "review_priority"
        in dataframe.columns
    ):
        priority_column = (
            "review_priority"
        )

    elif (
        "priority"
        in dataframe.columns
    ):
        priority_column = (
            "priority"
        )

    if priority_column is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "Candidate table does not contain "
                "a priority column."
            ),
        )

    normalized_priority = (
        priority
        .strip()
        .lower()
        .replace(
            " ",
            "_",
        )
    )

    aliases = {
        "higher":
            "higher_priority_candidate",

        "high":
            "higher_priority_candidate",

        "higher_priority":
            "higher_priority_candidate",

        "moderate":
            "moderate_priority_candidate",

        "medium":
            "moderate_priority_candidate",

        "moderate_priority":
            "moderate_priority_candidate",

        "lower":
            "lower_priority_candidate",

        "low":
            "lower_priority_candidate",

        "lower_priority":
            "lower_priority_candidate",
    }

    normalized_priority = (
        aliases.get(
            normalized_priority,
            normalized_priority,
        )
    )

    matches = dataframe[
        dataframe[
            priority_column
        ]
        .astype(str)
        .str.strip()
        .str.lower()
        == normalized_priority
    ]

    return {
        "priority":
            normalized_priority,

        "count":
            len(
                matches
            ),

        "candidates":
            dataframe_records(
                matches
            ),
    }


# =============================================================================
# CANDIDATE CARDS
# =============================================================================

@app.get(
    "/api/candidate-cards"
)
def candidate_cards():
    return load_json(
        FILES[
            "candidate_cards"
        ]
    )


# =============================================================================
# APPLICATION METADATA
# =============================================================================

@app.get(
    "/api/metadata"
)
def metadata():
    return load_json(
        FILES[
            "metadata"
        ]
    )


# =============================================================================
# ANALYTICAL SAFETY
# =============================================================================

@app.get(
    "/api/safety"
)
def analytical_safety():
    metadata_data = (
        load_json(
            FILES[
                "metadata"
            ]
        )
    )

    return {
        "analytical_restrictions":
            metadata_data.get(
                "analytical_restrictions",
                {},
            ),

        "limitations":
            metadata_data.get(
                "limitations",
                [],
            ),

        "reporting_scope":
            metadata_data.get(
                "reporting_scope"
            ),

        "frontend_warning":
            metadata_data.get(
                "frontend_warning"
            ),

        "comparator_warning":
            metadata_data.get(
                "comparator_warning"
            ),

        "disproportionality_warning":
            metadata_data.get(
                "disproportionality_warning"
            ),

        "interaction_warning":
            metadata_data.get(
                "interaction_warning"
            ),
    }


# =============================================================================
# FULL APPLICATION PAYLOAD
# =============================================================================

@app.get(
    "/api/payload"
)
def full_payload():
    return load_json(
        FILES[
            "api_payload"
        ]
    )


# =============================================================================
# GENERATED REPORT JSON
# =============================================================================

@app.get(
    "/api/report/json"
)
def report_json():
    return load_json(
        FILES[
            "generated_report"
        ]
    )


# =============================================================================
# HUMAN-READABLE REPORT
# =============================================================================

@app.get(
    "/api/report/text",
    response_class=PlainTextResponse,
)
def report_text():
    path = FILES[
        "report"
    ]

    if not path.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                "Human-readable report "
                "is unavailable."
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


# =============================================================================
# APPLICATION INFO
# =============================================================================

@app.get(
    "/api/info"
)
def application_info():
    dashboard_data = (
        load_json(
            FILES[
                "dashboard"
            ]
        )
    )

    if (
        DATA_DIR
        == RELEASE_DATA_DIR
    ):
        data_source_type = (
            "validated_release"
        )

    elif (
        DATA_DIR
        == APP_DATA_DIR
    ):
        data_source_type = (
            "deployment_app_data"
        )

    else:
        data_source_type = (
            "development_data"
        )

    return {
        "application":
            "GenAR-PADER-AI",

        "version":
            "1.0.0",

        "pipeline_phases":
            12,

        "pipeline_status":
            "complete",

        "integrated_cases":
            dashboard_data.get(
                "total_safety_reports"
            ),

        "candidate_reactions":
            dashboard_data.get(
                "candidate_reactions"
            ),

        "top_candidate":
            dashboard_data.get(
                "top_candidate"
            ),

        "data_source":
            data_source_type,

        "data_directory":
            str(
                DATA_DIR
            ),

        "genai": {
            "enabled":
                True,

            "status_endpoint":
                "/api/assistant/status",

            "chat_endpoint":
                "/api/assistant/chat",
        },
    }