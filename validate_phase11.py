import os
import json
import sys
import pandas as pd


# =============================================================================
# PHASE 11 - APPLICATION / DASHBOARD OUTPUT VALIDATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


FILES = {
    "dashboard": "phase11_dashboard_summary.json",
    "table": "phase11_candidate_table.csv",
    "cards": "phase11_candidate_cards.json",
    "metadata": "phase11_application_metadata.json",
    "api": "phase11_api_payload.json",
}


# =============================================================================
# HELPERS
# =============================================================================

def section(title):
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


def pass_msg(message):
    print(f"PASS - {message}")


def fail(message):
    print(f"FAIL - {message}")
    sys.exit(1)


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        fail(
            f"Unable to read {os.path.basename(path)}: {exc}"
        )


def as_bool(value):
    if isinstance(value, bool):
        return value

    if value is None:
        return None

    text = str(value).strip().lower()

    if text in {"true", "yes", "1"}:
        return True

    if text in {"false", "no", "0"}:
        return False

    return None


# =============================================================================
# START
# =============================================================================

section(
    "PHASE 11 - APPLICATION & DASHBOARD OUTPUT VALIDATION"
)


# =============================================================================
# FILE CHECK
# =============================================================================

section("FILE CHECK")

paths = {}

for key, filename in FILES.items():

    path = os.path.join(
        DATA_DIR,
        filename
    )

    paths[key] = path

    if not os.path.exists(path):
        fail(
            f"Required Phase 11 file missing: {filename}"
        )

    if os.path.getsize(path) == 0:
        fail(
            f"Required Phase 11 file is empty: {filename}"
        )

    pass_msg(filename)


# =============================================================================
# LOAD OUTPUTS
# =============================================================================

section("LOADING PHASE 11 OUTPUTS")

dashboard = load_json(
    paths["dashboard"]
)

candidate_table = pd.read_csv(
    paths["table"]
)

cards = load_json(
    paths["cards"]
)

metadata = load_json(
    paths["metadata"]
)

api_payload = load_json(
    paths["api"]
)


print(
    f"Dashboard schema      : "
    f"{dashboard.get('schema_version')}"
)

print(
    f"Candidate table rows  : "
    f"{len(candidate_table)}"
)

print(
    f"Candidate cards       : "
    f"{cards.get('candidate_count')}"
)

print(
    f"Metadata schema       : "
    f"{metadata.get('schema_version')}"
)

print(
    f"API version           : "
    f"{api_payload.get('api_version')}"
)


# =============================================================================
# VERSION VALIDATION
# =============================================================================

section("VERSION VALIDATION")

if (
    dashboard.get("schema_version")
    != "phase11_dashboard_v1"
):
    fail(
        "Unexpected dashboard schema version."
    )

pass_msg(
    "Dashboard schema version valid."
)


if (
    cards.get("schema_version")
    != "phase11_candidate_cards_v1"
):
    fail(
        "Unexpected candidate-card schema version."
    )

pass_msg(
    "Candidate-card schema version valid."
)


if (
    metadata.get("schema_version")
    != "phase11_metadata_v1"
):
    fail(
        "Unexpected metadata schema version."
    )

pass_msg(
    "Metadata schema version valid."
)


if (
    api_payload.get("api_version")
    != "phase11_api_v1"
):
    fail(
        "Unexpected API version."
    )

pass_msg(
    "API version valid."
)


# =============================================================================
# DASHBOARD SUMMARY VALIDATION
# =============================================================================

section("DASHBOARD SUMMARY VALIDATION")

expected_dashboard_values = {
    "phase": 11,
    "total_safety_reports": 1024,
    "bisoprolol_cases": 1024,
    "candidate_reactions": 8,
}


for key, expected in expected_dashboard_values.items():

    actual = dashboard.get(key)

    if actual != expected:
        fail(
            f"{key}: expected {expected}, "
            f"found {actual}"
        )

    pass_msg(
        f"{key}: {expected}"
    )


priority_distribution = dashboard.get(
    "priority_distribution",
    {}
)

expected_priorities = {
    "higher_priority_candidate": 1,
    "moderate_priority_candidate": 2,
    "lower_priority_candidate": 5,
}


for priority, expected in (
    expected_priorities.items()
):

    actual = priority_distribution.get(
        priority
    )

    if actual != expected:
        fail(
            f"{priority}: expected {expected}, "
            f"found {actual}"
        )

    pass_msg(
        f"{priority}: {expected}"
    )


# =============================================================================
# TOP CANDIDATE VALIDATION
# =============================================================================

section("TOP CANDIDATE VALIDATION")

top_candidate = dashboard.get(
    "top_candidate",
    {}
)


if (
    top_candidate.get("reaction")
    != "Acute kidney injury"
):
    fail(
        "Unexpected top candidate."
    )

pass_msg(
    "Top candidate: Acute kidney injury"
)


if (
    top_candidate.get("reported_cases")
    != 22
):
    fail(
        "Unexpected top candidate case count."
    )

pass_msg(
    "Top candidate cases: 22"
)


if (
    top_candidate.get("priority")
    != "higher_priority_candidate"
):
    fail(
        "Unexpected top candidate priority."
    )

pass_msg(
    "Top candidate priority valid."
)


# =============================================================================
# CANDIDATE TABLE VALIDATION
# =============================================================================

section("CANDIDATE TABLE VALIDATION")

required_table_columns = [
    "rank",
    "reaction",
    "reported_cases",
    "percentage_of_all_cases",
    "serious_cases",
    "serious_percentage",
    "death_cases",
    "hospitalization_cases",
    "evidence_level",
    "review_priority",
    "recommended_action",
    "requires_case_review",
    "frequency_is_incidence",
    "causality_established",
    "disproportionality_established",
    "confirmed_signal_established",
    "interaction_established",
]


for column in required_table_columns:

    if column not in candidate_table.columns:
        fail(
            f"Candidate table missing column: {column}"
        )

    pass_msg(
        f"Candidate table column: {column}"
    )


if len(candidate_table) != 8:
    fail(
        f"Expected 8 candidate table rows, "
        f"found {len(candidate_table)}."
    )

pass_msg(
    "Candidate table contains 8 rows."
)


# =============================================================================
# RANK VALIDATION
# =============================================================================

section("RANK VALIDATION")

ranks = (
    pd.to_numeric(
        candidate_table["rank"],
        errors="coerce"
    )
    .astype("Int64")
)


if ranks.isna().any():
    fail(
        "Candidate table contains invalid rank values."
    )


actual_ranks = ranks.astype(int).tolist()

expected_ranks = list(
    range(1, 9)
)


if actual_ranks != expected_ranks:
    fail(
        f"Invalid rank sequence: {actual_ranks}"
    )

pass_msg(
    "Candidate ranks are contiguous from 1 to 8."
)


# =============================================================================
# CANDIDATE VALUE VALIDATION
# =============================================================================

section("CANDIDATE VALUE VALIDATION")

expected_candidates = {
    "Acute kidney injury": {
        "rank": 1,
        "reported_cases": 22,
        "priority":
            "higher_priority_candidate",
    },

    "Drug ineffective": {
        "rank": 2,
        "reported_cases": 11,
        "priority":
            "moderate_priority_candidate",
    },

    "Cholestasis": {
        "rank": 3,
        "reported_cases": 6,
        "priority":
            "lower_priority_candidate",
    },

    "Hypokalaemia": {
        "rank": 4,
        "reported_cases": 6,
        "priority":
            "moderate_priority_candidate",
    },

    "Hyponatraemia": {
        "rank": 5,
        "reported_cases": 6,
        "priority":
            "lower_priority_candidate",
    },

    "Drug interaction": {
        "rank": 6,
        "reported_cases": 5,
        "priority":
            "lower_priority_candidate",
    },

    "Hepatic cytolysis": {
        "rank": 7,
        "reported_cases": 5,
        "priority":
            "lower_priority_candidate",
    },

    "Joint swelling": {
        "rank": 8,
        "reported_cases": 5,
        "priority":
            "lower_priority_candidate",
    },
}


for reaction, expected in (
    expected_candidates.items()
):

    rows = candidate_table[
        candidate_table[
            "reaction"
        ] == reaction
    ]

    if len(rows) != 1:
        fail(
            f"Expected exactly one row for "
            f"{reaction}."
        )

    row = rows.iloc[0]

    if int(row["rank"]) != expected["rank"]:
        fail(
            f"{reaction}: rank mismatch."
        )

    if (
        int(row["reported_cases"])
        != expected["reported_cases"]
    ):
        fail(
            f"{reaction}: case-count mismatch."
        )

    if (
        row["review_priority"]
        != expected["priority"]
    ):
        fail(
            f"{reaction}: priority mismatch."
        )

    pass_msg(
        f"{reaction}: values match."
    )


# =============================================================================
# CANDIDATE CARD VALIDATION
# =============================================================================

section("CANDIDATE CARD VALIDATION")

candidate_cards = cards.get(
    "cards",
    []
)


if len(candidate_cards) != 8:
    fail(
        f"Expected 8 candidate cards, "
        f"found {len(candidate_cards)}."
    )

pass_msg(
    "Eight candidate cards available."
)


card_names = {
    card.get("reaction")
    for card in candidate_cards
}

table_names = set(
    candidate_table[
        "reaction"
    ].tolist()
)


if card_names != table_names:
    fail(
        "Candidate-card and table reaction sets differ."
    )

pass_msg(
    "Candidate-card and table reaction sets match."
)


# =============================================================================
# CARD SAFETY VALIDATION
# =============================================================================

section("CANDIDATE CARD SAFETY VALIDATION")

card_false_flags = [
    "frequency_is_incidence",
    "confirmed_signal",
    "confirmed_adverse_reaction",
    "causality_established",
    "disproportionality_established",
    "interaction_established",
]


for card in candidate_cards:

    reaction = card.get(
        "reaction",
        "[UNKNOWN]"
    )

    boundaries = card.get(
        "analytical_boundaries",
        {}
    )

    for flag in card_false_flags:

        if flag not in boundaries:
            fail(
                f"{reaction}: missing safety flag "
                f"{flag}"
            )

        value = as_bool(
            boundaries[flag]
        )

        if value is not False:
            fail(
                f"{reaction}: unsafe safety flag "
                f"{flag}={value}"
            )


pass_msg(
    "All candidate-card analytical boundaries remain False."
)


# =============================================================================
# TABLE SAFETY VALIDATION
# =============================================================================

section("CANDIDATE TABLE SAFETY VALIDATION")

table_false_columns = [
    "frequency_is_incidence",
    "causality_established",
    "disproportionality_established",
    "confirmed_signal_established",
    "interaction_established",
]


for column in table_false_columns:

    values = (
        candidate_table[column]
        .apply(as_bool)
    )

    if values.isna().any():
        fail(
            f"Invalid boolean value in "
            f"{column}"
        )

    if values.any():
        fail(
            f"Unsafe True value detected in "
            f"{column}"
        )

    pass_msg(
        f"{column} remains False."
    )


# =============================================================================
# METADATA VALIDATION
# =============================================================================

section("APPLICATION METADATA VALIDATION")

if (
    metadata.get("current_phase")
    != 11
):
    fail(
        "Application metadata current phase "
        "is not 11."
    )

pass_msg(
    "Metadata current phase: 11"
)


dataset_metadata = metadata.get(
    "dataset",
    {}
)


if (
    dataset_metadata.get(
        "integrated_cases"
    )
    != 1024
):
    fail(
        "Metadata integrated case count mismatch."
    )


if (
    dataset_metadata.get(
        "bisoprolol_cases"
    )
    != 1024
):
    fail(
        "Metadata Bisoprolol case count mismatch."
    )


if (
    dataset_metadata.get(
        "candidate_reactions"
    )
    != 8
):
    fail(
        "Metadata candidate count mismatch."
    )


pass_msg(
    "Metadata dataset counts are valid."
)


# =============================================================================
# METADATA SAFETY VALIDATION
# =============================================================================

section("METADATA SAFETY VALIDATION")

metadata_restrictions = metadata.get(
    "analytical_restrictions",
    {}
)


metadata_false_flags = [
    "comparator_available",
    "ror_available",
    "prr_available",
    "frequency_is_incidence",
    "causality_established",
    "disproportionality_established",
    "confirmed_signal_established",
    "drug_interaction_established",
]


for flag in metadata_false_flags:

    if flag not in metadata_restrictions:
        fail(
            f"Metadata missing safety flag: {flag}"
        )

    value = as_bool(
        metadata_restrictions[flag]
    )

    if value is not False:
        fail(
            f"Metadata safety violation: "
            f"{flag}={value}"
        )

    pass_msg(
        f"{flag} remains False."
    )


# =============================================================================
# API STRUCTURE VALIDATION
# =============================================================================

section("API PAYLOAD VALIDATION")

if (
    api_payload.get("status")
    != "success"
):
    fail(
        "API payload status is not success."
    )

pass_msg(
    "API payload status: success"
)


if api_payload.get("phase") != 11:
    fail(
        "API payload phase is not 11."
    )

pass_msg(
    "API payload phase: 11"
)


api_data = api_payload.get(
    "data",
    {}
)


required_api_sections = [
    "dashboard",
    "candidate_table",
    "candidate_cards",
    "limitations",
    "analytical_safety",
]


for api_section in required_api_sections:

    if api_section not in api_data:
        fail(
            f"API data missing section: "
            f"{api_section}"
        )

    pass_msg(
        f"API data section: {api_section}"
    )


# =============================================================================
# API CANDIDATE COUNT
# =============================================================================

section("API CANDIDATE COUNT VALIDATION")


if (
    len(
        api_data[
            "candidate_table"
        ]
    )
    != 8
):
    fail(
        "API candidate table must contain "
        "8 rows."
    )


if (
    len(
        api_data[
            "candidate_cards"
        ]
    )
    != 8
):
    fail(
        "API candidate cards must contain "
        "8 records."
    )


pass_msg(
    "API candidate counts are valid."
)


# =============================================================================
# FRONTEND DISPLAY SAFETY
# =============================================================================

section("FRONTEND DISPLAY SAFETY VALIDATION")

display = api_payload.get(
    "display",
    {}
)


unsafe_display_flags = [
    "show_ror",
    "show_prr",
    "show_incidence",
    "show_causality_claim",
    "show_confirmed_signal",
    "show_confirmed_interaction",
]


for flag in unsafe_display_flags:

    if flag not in display:
        fail(
            f"Display configuration missing: {flag}"
        )

    value = as_bool(
        display[flag]
    )

    if value is not False:
        fail(
            f"Unsafe frontend display flag "
            f"enabled: {flag}"
        )

    pass_msg(
        f"{flag} remains disabled."
    )


allowed_display_flags = [
    "show_reported_frequency",
    "show_seriousness",
    "show_review_priority",
    "show_follow_up_recommendation",
    "show_limitations",
]


for flag in allowed_display_flags:

    if flag not in display:
        fail(
            f"Display configuration missing: {flag}"
        )

    value = as_bool(
        display[flag]
    )

    if value is not True:
        fail(
            f"Expected descriptive frontend "
            f"field disabled: {flag}"
        )

    pass_msg(
        f"{flag} enabled."
    )


# =============================================================================
# LIMITATION VALIDATION
# =============================================================================

section("LIMITATION VALIDATION")

api_limitations = api_data.get(
    "limitations",
    []
)


if len(api_limitations) != 5:
    fail(
        f"Expected 5 limitations in API payload, "
        f"found {len(api_limitations)}."
    )

pass_msg(
    "Five analytical limitations retained."
)


for index, limitation in enumerate(
    api_limitations,
    start=1
):

    for field in [
        "limitation_id",
        "limitation",
        "impact",
        "restriction",
    ]:

        if field not in limitation:
            fail(
                f"Limitation {index} missing "
                f"field: {field}"
            )


pass_msg(
    "Limitation structures are complete."
)


# =============================================================================
# WARNING VALIDATION
# =============================================================================

section("API WARNING VALIDATION")

warnings = api_payload.get(
    "warnings",
    []
)


if len(warnings) < 5:
    fail(
        "API payload contains too few "
        "analytical warnings."
    )


warning_text = " ".join(
    str(item).lower()
    for item in warnings
)


required_warning_concepts = [
    "not incidence",
    "comparator",
    "ror",
    "prr",
    "causality",
    "review priority",
]


for concept in required_warning_concepts:

    if concept not in warning_text:
        fail(
            f"API warning concept missing: "
            f"{concept}"
        )

    pass_msg(
        f"Warning concept: {concept}"
    )


# =============================================================================
# OUTPUT SIZE VALIDATION
# =============================================================================

section("OUTPUT SIZE VALIDATION")

for filename in FILES.values():

    path = os.path.join(
        DATA_DIR,
        filename
    )

    size = os.path.getsize(
        path
    )

    print(
        f"{filename:<40} "
        f"{size:>10,} bytes"
    )

    if size == 0:
        fail(
            f"Output file empty: {filename}"
        )


pass_msg(
    "All Phase 11 output files are non-empty."
)


# =============================================================================
# FINAL ANALYTICAL SAFETY
# =============================================================================

section("FINAL ANALYTICAL SAFETY")

print(
    "Comparator cohort available          : NO"
)

print(
    "ROR calculated                        : NO"
)

print(
    "PRR calculated                        : NO"
)

print(
    "Frequency interpreted as incidence   : NO"
)

print(
    "Causality established                : NO"
)

print(
    "Disproportionality established       : NO"
)

print(
    "Confirmed safety signal established  : NO"
)

print(
    "Drug-drug interaction established    : NO"
)


# =============================================================================
# FINAL RESULT
# =============================================================================

section("FINAL RESULT")

print("PASS")

print()

print(
    "Phase 11 application/dashboard output "
    "package is structurally valid."
)

print()

print("Validated outputs:")

print(
    "- phase11_dashboard_summary.json"
)

print(
    "- phase11_candidate_table.csv"
)

print(
    "- phase11_candidate_cards.json"
)

print(
    "- phase11_application_metadata.json"
)

print(
    "- phase11_api_payload.json"
)

print()

print("Phase status:")

print(
    "Phase 1  - Drug normalization        : COMPLETE"
)

print(
    "Phase 2  - Reaction normalization    : COMPLETE"
)

print(
    "Phase 3  - Structure validation      : COMPLETE"
)

print(
    "Phase 4  - Case integration          : COMPLETE"
)

print(
    "Phase 5  - Pharmacovigilance screen  : COMPLETE"
)

print(
    "Phase 6  - Signal pattern analysis   : COMPLETE"
)

print(
    "Phase 7  - Evidence & reporting      : COMPLETE"
)

print(
    "Phase 8  - Structured reporting      : COMPLETE"
)

print(
    "Phase 9  - Decision support          : COMPLETE"
)

print(
    "Phase 10 - Controlled reporting      : COMPLETE"
)

print(
    "Phase 11 - Application output        : COMPLETE"
)

print()

print(
    "Only Phase 12 remains."
)

print()

print(
    "Phase 12 will perform final end-to-end "
    "pipeline validation and release packaging."
)

print()

print("=" * 100)