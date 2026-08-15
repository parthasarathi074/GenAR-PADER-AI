import os
import json
import pandas as pd
from datetime import datetime, timezone


# =============================================================================
# PHASE 11 - APPLICATION / DASHBOARD OUTPUT ANALYSIS
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)


INPUT_FILES = {
    "context": "phase10_genai_context.json",
    "candidate_context": "phase10_candidate_context.json",
    "reporting_rules": "phase10_reporting_rules.json",
    "generated_report": "phase10_generated_report.json",
    "text_report": "phase10_pharmacovigilance_report.txt",
}


OUTPUT_FILES = {
    "dashboard":
        "phase11_dashboard_summary.json",

    "table":
        "phase11_candidate_table.csv",

    "cards":
        "phase11_candidate_cards.json",

    "metadata":
        "phase11_application_metadata.json",

    "api":
        "phase11_api_payload.json",
}


# =============================================================================
# HELPERS
# =============================================================================

def header(title):
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


def section(title):
    print()
    print("=" * 100)
    print(title)
    print("-" * 100)


def pass_msg(message):
    print(f"PASS - {message}")


def fail(message):
    print(f"FAIL - {message}")
    raise SystemExit(1)


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        fail(
            f"Unable to load "
            f"{os.path.basename(path)}: {exc}"
        )


def load_text(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as exc:
        fail(
            f"Unable to load "
            f"{os.path.basename(path)}: {exc}"
        )


def write_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )
    except Exception as exc:
        fail(
            f"Unable to write "
            f"{os.path.basename(path)}: {exc}"
        )


def as_bool(value):

    if isinstance(value, bool):
        return value

    if value is None:
        return None

    value = str(value).strip().lower()

    if value in {
        "true",
        "yes",
        "1"
    }:
        return True

    if value in {
        "false",
        "no",
        "0"
    }:
        return False

    return None


def safe_number(value, default=0):

    try:
        if pd.isna(value):
            return default

        return value

    except Exception:
        return default


# =============================================================================
# START
# =============================================================================

header(
    "PHASE 11 - APPLICATION & DASHBOARD OUTPUT ANALYSIS"
)


# =============================================================================
# FILE CHECK
# =============================================================================

section("FILE CHECK")

paths = {}

for key, filename in INPUT_FILES.items():

    path = os.path.join(
        DATA_DIR,
        filename
    )

    paths[key] = path

    if not os.path.exists(path):
        fail(
            f"Required Phase 10 file missing: "
            f"{filename}"
        )

    if os.path.getsize(path) == 0:
        fail(
            f"Required Phase 10 file is empty: "
            f"{filename}"
        )

    pass_msg(filename)


# =============================================================================
# LOAD PHASE 10 DATA
# =============================================================================

section("LOADING PHASE 10 OUTPUTS")

context = load_json(
    paths["context"]
)

candidate_context = load_json(
    paths["candidate_context"]
)

reporting_rules = load_json(
    paths["reporting_rules"]
)

generated_report = load_json(
    paths["generated_report"]
)

text_report = load_text(
    paths["text_report"]
)


dataset_summary = generated_report.get(
    "dataset_summary",
    {}
)

candidates = generated_report.get(
    "candidates",
    []
)

limitations = generated_report.get(
    "limitations",
    []
)

analytical_safety = generated_report.get(
    "analytical_safety",
    {}
)


print(
    f"Context version       : "
    f"{context.get('context_version')}"
)

print(
    f"Report version        : "
    f"{generated_report.get('report_version')}"
)

print(
    f"Integrated cases      : "
    f"{dataset_summary.get('integrated_cases'):,}"
)

print(
    f"Candidate reactions   : "
    f"{len(candidates)}"
)

print(
    f"Analytical limitations: "
    f"{len(limitations)}"
)


# =============================================================================
# INPUT STRUCTURE VALIDATION
# =============================================================================

section("INPUT STRUCTURE VALIDATION")

if len(candidates) != 8:
    fail(
        f"Expected 8 candidate reactions, "
        f"found {len(candidates)}."
    )

pass_msg(
    "Eight candidate reactions available."
)


if len(limitations) != 5:
    fail(
        f"Expected 5 analytical limitations, "
        f"found {len(limitations)}."
    )

pass_msg(
    "Five analytical limitations available."
)


required_candidate_fields = [
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
    "evidence_summary",
    "follow_up_recommendation",
    "interpretation_scope",
    "requires_case_review",
    "confirmed_signal",
    "confirmed_adverse_reaction",
    "causality_established",
    "disproportionality_established",
    "incidence_established",
    "interaction_established",
]


for candidate in candidates:

    reaction = candidate.get(
        "reaction",
        "[UNKNOWN]"
    )

    missing = [
        field
        for field in required_candidate_fields
        if field not in candidate
    ]

    if missing:
        fail(
            f"{reaction} missing required fields: "
            f"{missing}"
        )


pass_msg(
    "All candidate fields available."
)


# =============================================================================
# ANALYTICAL SAFETY GATE
# =============================================================================

section("ANALYTICAL SAFETY GATE")

required_false_flags = [
    "comparator_available",
    "ror_available",
    "prr_available",
    "frequency_is_incidence",
    "causality_established",
    "disproportionality_established",
    "confirmed_signal_established",
    "drug_interaction_established",
]


for flag in required_false_flags:

    if flag not in analytical_safety:
        fail(
            f"Missing analytical safety flag: "
            f"{flag}"
        )

    value = as_bool(
        analytical_safety[flag]
    )

    print(
        f"{flag:<40}: {value}"
    )

    if value is not False:
        fail(
            f"Analytical safety violation: "
            f"{flag}={value}"
        )


pass_msg(
    "Analytical restrictions preserved."
)


# =============================================================================
# SORT CANDIDATES
# =============================================================================

candidates = sorted(
    candidates,
    key=lambda item: int(item["rank"])
)


# =============================================================================
# BUILD DASHBOARD SUMMARY
# =============================================================================

section("BUILDING DASHBOARD SUMMARY")

priority_distribution = {
    "higher_priority_candidate": 0,
    "moderate_priority_candidate": 0,
    "lower_priority_candidate": 0,
}


for candidate in candidates:

    priority = candidate[
        "review_priority"
    ]

    if priority not in priority_distribution:
        priority_distribution[priority] = 0

    priority_distribution[priority] += 1


dashboard_summary = {
    "phase": 11,
    "schema_version": "phase11_dashboard_v1",

    "source_context_version":
        context.get("context_version"),

    "source_report_version":
        generated_report.get("report_version"),

    "analysis_scope":
        "descriptive_exploratory_decision_support",

    "total_safety_reports":
        int(dataset_summary["integrated_cases"]),

    "bisoprolol_cases":
        int(dataset_summary["bisoprolol_cases"]),

    "candidate_reactions":
        int(dataset_summary["candidate_reactions"]),

    "priority_distribution":
        priority_distribution,

    "top_candidate": {
        "reaction":
            dataset_summary["top_candidate"],

        "reported_cases":
            int(
                dataset_summary[
                    "top_candidate_cases"
                ]
            ),

        "priority":
            dataset_summary[
                "top_candidate_priority"
            ],
    },

    "analytical_status": {
        "comparator_available": False,
        "ror_available": False,
        "prr_available": False,
        "frequency_is_incidence": False,
        "causality_established": False,
        "disproportionality_established": False,
        "confirmed_signal_established": False,
        "drug_interaction_established": False,
    },

    "interpretation":
        "Dashboard metrics summarize reported "
        "case patterns and review priorities only.",

    "priority_interpretation":
        "Review priority is a triage classification "
        "and does not represent a confirmed safety signal.",
}


dashboard_path = os.path.join(
    DATA_DIR,
    OUTPUT_FILES["dashboard"]
)

write_json(
    dashboard_path,
    dashboard_summary
)

pass_msg(
    "Dashboard summary created:"
)

print(
    dashboard_path
)


# =============================================================================
# BUILD CANDIDATE TABLE
# =============================================================================

section("BUILDING CANDIDATE TABLE")

candidate_table_rows = []


for candidate in candidates:

    candidate_table_rows.append(
        {
            "rank":
                int(candidate["rank"]),

            "reaction":
                candidate["reaction"],

            "reported_cases":
                int(candidate["reported_cases"]),

            "percentage_of_all_cases":
                float(
                    candidate[
                        "percentage_of_all_cases"
                    ]
                ),

            "serious_cases":
                int(candidate["serious_cases"]),

            "serious_percentage":
                float(
                    candidate[
                        "serious_percentage"
                    ]
                ),

            "death_cases":
                int(candidate["death_cases"]),

            "hospitalization_cases":
                int(
                    candidate[
                        "hospitalization_cases"
                    ]
                ),

            "evidence_level":
                candidate["evidence_level"],

            "review_priority":
                candidate["review_priority"],

            "recommended_action":
                candidate["recommended_action"],

            "requires_case_review":
                bool(
                    candidate[
                        "requires_case_review"
                    ]
                ),

            "frequency_is_incidence":
                False,

            "causality_established":
                False,

            "disproportionality_established":
                False,

            "confirmed_signal_established":
                False,

            "interaction_established":
                False,
        }
    )


candidate_table = pd.DataFrame(
    candidate_table_rows
)


candidate_table_path = os.path.join(
    DATA_DIR,
    OUTPUT_FILES["table"]
)


candidate_table.to_csv(
    candidate_table_path,
    index=False,
    encoding="utf-8"
)


pass_msg(
    "Candidate table created:"
)

print(
    candidate_table_path
)


# =============================================================================
# BUILD CANDIDATE DETAIL CARDS
# =============================================================================

section("BUILDING CANDIDATE DETAIL CARDS")

candidate_cards = []


for candidate in candidates:

    card = {
        "rank":
            int(candidate["rank"]),

        "reaction":
            candidate["reaction"],

        "metrics": {
            "reported_cases":
                int(candidate["reported_cases"]),

            "percentage_of_all_cases":
                float(
                    candidate[
                        "percentage_of_all_cases"
                    ]
                ),

            "serious_cases":
                int(candidate["serious_cases"]),

            "serious_percentage":
                float(
                    candidate[
                        "serious_percentage"
                    ]
                ),

            "death_cases":
                int(candidate["death_cases"]),

            "hospitalization_cases":
                int(
                    candidate[
                        "hospitalization_cases"
                    ]
                ),
        },

        "classification": {
            "evidence_level":
                candidate["evidence_level"],

            "review_priority":
                candidate["review_priority"],

            "requires_case_review":
                bool(
                    candidate[
                        "requires_case_review"
                    ]
                ),
        },

        "evidence_summary":
            candidate["evidence_summary"],

        "recommended_action":
            candidate["recommended_action"],

        "follow_up_recommendation":
            candidate[
                "follow_up_recommendation"
            ],

        "interpretation_scope":
            candidate["interpretation_scope"],

        "analytical_boundaries": {
            "frequency_is_incidence":
                False,

            "confirmed_signal":
                False,

            "confirmed_adverse_reaction":
                False,

            "causality_established":
                False,

            "disproportionality_established":
                False,

            "interaction_established":
                False,
        },
    }

    candidate_cards.append(card)


cards_output = {
    "schema_version":
        "phase11_candidate_cards_v1",

    "candidate_count":
        len(candidate_cards),

    "cards":
        candidate_cards,
}


cards_path = os.path.join(
    DATA_DIR,
    OUTPUT_FILES["cards"]
)


write_json(
    cards_path,
    cards_output
)


pass_msg(
    "Candidate detail cards created:"
)

print(
    cards_path
)


# =============================================================================
# BUILD APPLICATION METADATA
# =============================================================================

section("BUILDING APPLICATION METADATA")

application_metadata = {
    "schema_version":
        "phase11_metadata_v1",

    "application_scope":
        "pharmacovigilance_decision_support",

    "source": {
        "phase": 10,
        "context_version":
            context.get("context_version"),
        "report_version":
            generated_report.get(
                "report_version"
            ),
    },

    "current_phase": 11,

    "dataset": {
        "integrated_cases":
            int(
                dataset_summary[
                    "integrated_cases"
                ]
            ),

        "bisoprolol_cases":
            int(
                dataset_summary[
                    "bisoprolol_cases"
                ]
            ),

        "candidate_reactions":
            len(candidates),
    },

    "analytical_restrictions": {
        "comparator_available": False,
        "ror_available": False,
        "prr_available": False,
        "frequency_is_incidence": False,
        "causality_established": False,
        "disproportionality_established": False,
        "confirmed_signal_established": False,
        "drug_interaction_established": False,
    },

    "limitations":
        limitations,

    "reporting_scope":
        "Descriptive and exploratory "
        "pharmacovigilance decision support.",

    "review_priority_definition":
        "Review priorities are triage categories "
        "for follow-up and do not establish "
        "causality or confirmed safety signals.",

    "frontend_warning":
        "Reported case frequency must not be "
        "displayed or interpreted as incidence.",

    "comparator_warning":
        "No internal non-Bisoprolol comparator "
        "cohort is available.",

    "disproportionality_warning":
        "ROR and PRR are unavailable and must "
        "not be displayed as calculated metrics.",

    "interaction_warning":
        "Co-medication patterns are descriptive "
        "and do not establish drug-drug interactions.",
}


metadata_path = os.path.join(
    DATA_DIR,
    OUTPUT_FILES["metadata"]
)


write_json(
    metadata_path,
    application_metadata
)


pass_msg(
    "Application metadata created:"
)

print(
    metadata_path
)


# =============================================================================
# BUILD API PAYLOAD
# =============================================================================

section("BUILDING FRONTEND / API PAYLOAD")

api_payload = {
    "api_version":
        "phase11_api_v1",

    "status":
        "success",

    "phase":
        11,

    "data": {
        "dashboard":
            dashboard_summary,

        "candidate_table":
            candidate_table_rows,

        "candidate_cards":
            candidate_cards,

        "limitations":
            limitations,

        "analytical_safety":
            application_metadata[
                "analytical_restrictions"
            ],
    },

    "display": {
        "show_ror": False,
        "show_prr": False,
        "show_incidence": False,
        "show_causality_claim": False,
        "show_confirmed_signal": False,
        "show_confirmed_interaction": False,

        "show_reported_frequency": True,
        "show_seriousness": True,
        "show_review_priority": True,
        "show_follow_up_recommendation": True,
        "show_limitations": True,
    },

    "warnings": [
        "Reported frequency is not incidence.",

        "No internal non-Bisoprolol comparator "
        "is available.",

        "ROR and PRR were not calculated.",

        "Causality has not been established.",

        "Disproportionality has not been established.",

        "Review priority is a triage category only.",

        "Co-medication patterns do not establish "
        "drug-drug interactions.",
    ],
}


api_path = os.path.join(
    DATA_DIR,
    OUTPUT_FILES["api"]
)


write_json(
    api_path,
    api_payload
)


pass_msg(
    "Frontend/API payload created:"
)

print(
    api_path
)


# =============================================================================
# OUTPUT VALIDATION
# =============================================================================

section("OUTPUT CHECK")

for filename in OUTPUT_FILES.values():

    path = os.path.join(
        DATA_DIR,
        filename
    )

    if not os.path.exists(path):
        fail(
            f"Output file missing: {filename}"
        )

    if os.path.getsize(path) == 0:
        fail(
            f"Output file empty: {filename}"
        )

    pass_msg(filename)


# =============================================================================
# CANDIDATE COUNT CHECK
# =============================================================================

section("CANDIDATE COUNT CHECK")

print(
    f"Source candidates       : "
    f"{len(candidates)}"
)

print(
    f"Candidate table rows    : "
    f"{len(candidate_table)}"
)

print(
    f"Candidate cards         : "
    f"{len(candidate_cards)}"
)

print(
    f"API candidate rows      : "
    f"{len(api_payload['data']['candidate_table'])}"
)


if len(candidate_table) != len(candidates):
    fail(
        "Candidate table count mismatch."
    )

if len(candidate_cards) != len(candidates):
    fail(
        "Candidate card count mismatch."
    )

if (
    len(
        api_payload[
            "data"
        ][
            "candidate_table"
        ]
    )
    != len(candidates)
):
    fail(
        "API candidate count mismatch."
    )


pass_msg(
    "Candidate counts are consistent."
)


# =============================================================================
# RANK VALIDATION
# =============================================================================

section("RANK VALIDATION")

expected_ranks = list(
    range(
        1,
        len(candidates) + 1
    )
)

actual_ranks = [
    int(candidate["rank"])
    for candidate in candidates
]


if actual_ranks != expected_ranks:
    fail(
        f"Candidate ranks are not contiguous: "
        f"{actual_ranks}"
    )


pass_msg(
    "Candidate ranking is contiguous."
)


# =============================================================================
# PRIORITY DISTRIBUTION VALIDATION
# =============================================================================

section("PRIORITY DISTRIBUTION")

for priority, count in (
    priority_distribution.items()
):

    print(
        f"{priority:<35}: {count}"
    )


if (
    sum(priority_distribution.values())
    != len(candidates)
):
    fail(
        "Priority distribution does not "
        "equal candidate count."
    )


pass_msg(
    "Priority distribution is valid."
)


# =============================================================================
# TOP CANDIDATE
# =============================================================================

section("TOP CANDIDATE")

top_candidate = candidates[0]


print(
    f"Reaction        : "
    f"{top_candidate['reaction']}"
)

print(
    f"Reported cases  : "
    f"{top_candidate['reported_cases']}"
)

print(
    f"Percentage      : "
    f"{float(top_candidate['percentage_of_all_cases']):.2f}%"
)

print(
    f"Serious cases   : "
    f"{top_candidate['serious_cases']}"
)

print(
    f"Priority        : "
    f"{top_candidate['review_priority']}"
)


if (
    top_candidate["reaction"]
    != dataset_summary["top_candidate"]
):
    fail(
        "Top candidate mismatch."
    )


if (
    int(top_candidate["reported_cases"])
    != int(
        dataset_summary[
            "top_candidate_cases"
        ]
    )
):
    fail(
        "Top candidate case-count mismatch."
    )


pass_msg(
    "Top candidate is consistent."
)


# =============================================================================
# APPLICATION SAFETY VALIDATION
# =============================================================================

section("APPLICATION SAFETY VALIDATION")

unsafe_display_flags = [
    "show_ror",
    "show_prr",
    "show_incidence",
    "show_causality_claim",
    "show_confirmed_signal",
    "show_confirmed_interaction",
]


for flag in unsafe_display_flags:

    value = api_payload[
        "display"
    ][flag]

    print(
        f"{flag:<35}: {value}"
    )

    if value is not False:
        fail(
            f"Unsafe frontend display "
            f"flag enabled: {flag}"
        )


pass_msg(
    "Unsafe analytical display options remain disabled."
)


allowed_display_flags = [
    "show_reported_frequency",
    "show_seriousness",
    "show_review_priority",
    "show_follow_up_recommendation",
    "show_limitations",
]


for flag in allowed_display_flags:

    value = api_payload[
        "display"
    ][flag]

    if value is not True:
        fail(
            f"Expected frontend display "
            f"flag disabled: {flag}"
        )


pass_msg(
    "Allowed descriptive display options are enabled."
)


# =============================================================================
# CANDIDATE SAFETY VALIDATION
# =============================================================================

section("CANDIDATE SAFETY VALIDATION")

candidate_false_flags = [
    "confirmed_signal",
    "confirmed_adverse_reaction",
    "causality_established",
    "disproportionality_established",
    "incidence_established",
    "interaction_established",
]


for candidate in candidates:

    reaction = candidate[
        "reaction"
    ]

    for flag in candidate_false_flags:

        value = as_bool(
            candidate.get(flag)
        )

        if value is not False:
            fail(
                f"Unsafe candidate state: "
                f"{reaction} -> "
                f"{flag}={value}"
            )


pass_msg(
    "All candidate safety restrictions preserved."
)


# =============================================================================
# DASHBOARD PREVIEW
# =============================================================================

section("DASHBOARD PREVIEW")

print(
    f"Total reports          : "
    f"{dashboard_summary['total_safety_reports']:,}"
)

print(
    f"Bisoprolol cases       : "
    f"{dashboard_summary['bisoprolol_cases']:,}"
)

print(
    f"Candidate reactions    : "
    f"{dashboard_summary['candidate_reactions']}"
)

print(
    f"Higher priority        : "
    f"{priority_distribution['higher_priority_candidate']}"
)

print(
    f"Moderate priority      : "
    f"{priority_distribution['moderate_priority_candidate']}"
)

print(
    f"Lower priority         : "
    f"{priority_distribution['lower_priority_candidate']}"
)

print(
    f"Top candidate          : "
    f"{dashboard_summary['top_candidate']['reaction']}"
)

print(
    f"Top candidate cases    : "
    f"{dashboard_summary['top_candidate']['reported_cases']}"
)


# =============================================================================
# CANDIDATE TABLE PREVIEW
# =============================================================================

section("CANDIDATE TABLE PREVIEW")

for row in candidate_table_rows:

    print(
        f"{row['rank']:02d}. "
        f"{row['reaction']:<35} "
        f"cases={row['reported_cases']:>3} "
        f"serious={row['serious_cases']:>3} "
        f"death={row['death_cases']:>2} "
        f"hosp={row['hospitalization_cases']:>3} "
        f"priority={row['review_priority']}"
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


print()
print(
    "Phase 11 transforms validated "
    "pharmacovigilance results into "
    "application-ready data only."
)

print(
    "No new analytical or causal "
    "conclusions are introduced."
)


# =============================================================================
# COMPLETE
# =============================================================================

header(
    "PHASE 11 ANALYSIS COMPLETE"
)

print(
    "Generated files:"
)

for filename in OUTPUT_FILES.values():

    print(
        f" - {filename}"
    )


print()
print(
    "Phase 11 application/dashboard "
    "data package is COMPLETE."
)

print()
print(
    "Next step:"
)

print(
    "validate_phase11.py"
)