import os
import json
import pandas as pd


# =============================================================================
# PHASE 11 - APPLICATION / DASHBOARD OUTPUT INVESTIGATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


INPUT_FILES = {
    "context": "phase10_genai_context.json",
    "candidate_context": "phase10_candidate_context.json",
    "reporting_rules": "phase10_reporting_rules.json",
    "generated_report": "phase10_generated_report.json",
    "text_report": "phase10_pharmacovigilance_report.txt",
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


def fail(message):
    print(f"FAIL - {message}")
    raise SystemExit(1)


def pass_msg(message):
    print(f"PASS - {message}")


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        fail(
            f"Unable to load {os.path.basename(path)}: {exc}"
        )


def load_text(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as exc:
        fail(
            f"Unable to load {os.path.basename(path)}: {exc}"
        )


def as_bool(value):
    if isinstance(value, bool):
        return value

    if value is None:
        return None

    value = str(value).strip().lower()

    if value in {"true", "yes", "1"}:
        return True

    if value in {"false", "no", "0"}:
        return False

    return None


# =============================================================================
# START
# =============================================================================

header(
    "PHASE 11 - APPLICATION & DASHBOARD OUTPUT INVESTIGATION"
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
            f"Required Phase 10 file missing: {filename}"
        )

    if os.path.getsize(path) == 0:
        fail(
            f"Required Phase 10 file is empty: {filename}"
        )

    pass_msg(filename)


# =============================================================================
# LOAD DATA
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


print(
    f"Context version       : "
    f"{context.get('context_version')}"
)

print(
    f"Report version        : "
    f"{generated_report.get('report_version')}"
)

print(
    f"Candidate count       : "
    f"{generated_report.get('candidate_count')}"
)

print(
    f"Text report length    : "
    f"{len(text_report):,} characters"
)


# =============================================================================
# DATASET SUMMARY
# =============================================================================

section("DATASET SUMMARY")

dataset_summary = generated_report.get(
    "dataset_summary",
    {}
)

required_summary_fields = [
    "integrated_cases",
    "bisoprolol_cases",
    "candidate_reactions",
    "higher_priority_candidates",
    "moderate_priority_candidates",
    "lower_priority_candidates",
    "top_candidate",
    "top_candidate_cases",
    "top_candidate_priority",
]


for field in required_summary_fields:

    if field not in dataset_summary:
        fail(
            f"Missing dataset-summary field: {field}"
        )

    pass_msg(
        f"dataset_summary: {field}"
    )


print()
print(
    f"Integrated cases       : "
    f"{dataset_summary['integrated_cases']:,}"
)

print(
    f"Bisoprolol cases       : "
    f"{dataset_summary['bisoprolol_cases']:,}"
)

print(
    f"Candidate reactions    : "
    f"{dataset_summary['candidate_reactions']}"
)

print(
    f"Higher priority        : "
    f"{dataset_summary['higher_priority_candidates']}"
)

print(
    f"Moderate priority      : "
    f"{dataset_summary['moderate_priority_candidates']}"
)

print(
    f"Lower priority         : "
    f"{dataset_summary['lower_priority_candidates']}"
)

print(
    f"Top candidate          : "
    f"{dataset_summary['top_candidate']}"
)

print(
    f"Top candidate cases    : "
    f"{dataset_summary['top_candidate_cases']}"
)


# =============================================================================
# CANDIDATE STRUCTURE INVESTIGATION
# =============================================================================

section("CANDIDATE STRUCTURE INVESTIGATION")

candidates = generated_report.get(
    "candidates",
    []
)

if len(candidates) != 8:
    fail(
        f"Expected 8 candidates, "
        f"found {len(candidates)}."
    )

pass_msg(
    "Eight candidate records available."
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
            f"{reaction} missing fields: {missing}"
        )


pass_msg(
    "All candidate records contain required fields."
)


# =============================================================================
# CANDIDATE INVENTORY
# =============================================================================

section("CANDIDATE INVENTORY")

sorted_candidates = sorted(
    candidates,
    key=lambda item: item["rank"]
)


for candidate in sorted_candidates:

    print(
        f"{int(candidate['rank']):02d}. "
        f"{candidate['reaction']:<35} "
        f"cases={int(candidate['reported_cases']):>3} "
        f"serious={int(candidate['serious_cases']):>3} "
        f"death={int(candidate['death_cases']):>2} "
        f"hosp={int(candidate['hospitalization_cases']):>3} "
        f"priority={candidate['review_priority']}"
    )


# =============================================================================
# DASHBOARD METRIC INVESTIGATION
# =============================================================================

section("DASHBOARD METRIC READINESS")

dashboard_metrics = {
    "total_cases":
        dataset_summary[
            "integrated_cases"
        ],

    "bisoprolol_cases":
        dataset_summary[
            "bisoprolol_cases"
        ],

    "candidate_count":
        dataset_summary[
            "candidate_reactions"
        ],

    "higher_priority_count":
        dataset_summary[
            "higher_priority_candidates"
        ],

    "moderate_priority_count":
        dataset_summary[
            "moderate_priority_candidates"
        ],

    "lower_priority_count":
        dataset_summary[
            "lower_priority_candidates"
        ],

    "top_candidate":
        dataset_summary[
            "top_candidate"
        ],

    "top_candidate_cases":
        dataset_summary[
            "top_candidate_cases"
        ],
}


for name, value in dashboard_metrics.items():

    print(
        f"{name:<30}: {value}"
    )


pass_msg(
    "Dashboard summary metrics available."
)


# =============================================================================
# CHART DATA READINESS
# =============================================================================

section("CHART DATA READINESS")

chart_fields = [
    "reaction",
    "reported_cases",
    "percentage_of_all_cases",
    "serious_cases",
    "death_cases",
    "hospitalization_cases",
    "review_priority",
]


for field in chart_fields:

    if not all(
        field in candidate
        for candidate in candidates
    ):
        fail(
            f"Chart field unavailable: {field}"
        )

    pass_msg(
        f"Chart field available: {field}"
    )


# =============================================================================
# TABLE DATA READINESS
# =============================================================================

section("CANDIDATE TABLE READINESS")

table_fields = [
    "rank",
    "reaction",
    "reported_cases",
    "percentage_of_all_cases",
    "serious_cases",
    "serious_percentage",
    "death_cases",
    "hospitalization_cases",
    "review_priority",
    "recommended_action",
]


for field in table_fields:

    if not all(
        field in candidate
        for candidate in candidates
    ):
        fail(
            f"Candidate-table field unavailable: {field}"
        )

    pass_msg(
        f"Candidate-table field available: {field}"
    )


# =============================================================================
# DETAIL CARD READINESS
# =============================================================================

section("CANDIDATE DETAIL CARD READINESS")

detail_fields = [
    "reaction",
    "evidence_summary",
    "follow_up_recommendation",
    "interpretation_scope",
    "review_priority",
    "requires_case_review",
]


for field in detail_fields:

    if not all(
        field in candidate
        for candidate in candidates
    ):
        fail(
            f"Detail-card field unavailable: {field}"
        )

    pass_msg(
        f"Detail-card field available: {field}"
    )


# =============================================================================
# LIMITATION DATA
# =============================================================================

section("LIMITATION DISPLAY READINESS")

limitations = generated_report.get(
    "limitations",
    []
)

if len(limitations) != 5:
    fail(
        f"Expected 5 analytical limitations, "
        f"found {len(limitations)}."
    )

pass_msg(
    "Five limitation records available."
)


for limitation in limitations:

    for field in [
        "limitation_id",
        "limitation",
        "impact",
        "restriction",
    ]:

        if field not in limitation:
            fail(
                f"Limitation record missing field: "
                f"{field}"
            )


pass_msg(
    "Limitation records are suitable for dashboard display."
)


# =============================================================================
# REPORT DISPLAY READINESS
# =============================================================================

section("TEXT REPORT DISPLAY READINESS")

required_report_sections = [
    "1. EXECUTIVE SUMMARY",
    "2. DATASET OVERVIEW",
    "3. METHODOLOGY OVERVIEW",
    "4. CANDIDATE REVIEW PRIORITY SUMMARY",
    "5. CANDIDATE-BY-CANDIDATE EVIDENCE",
    "6. SERIOUSNESS ASSESSMENT",
    "7. RECOMMENDED FOLLOW-UP ACTIONS",
    "8. ANALYTICAL LIMITATIONS",
    "9. INTERPRETATION BOUNDARIES",
    "10. FINAL PHARMACOVIGILANCE SUMMARY",
]


for report_section in required_report_sections:

    if report_section not in text_report:
        fail(
            f"Report section missing: "
            f"{report_section}"
        )

    pass_msg(
        report_section
    )


# =============================================================================
# ANALYTICAL SAFETY GATE
# =============================================================================

section("APPLICATION ANALYTICAL SAFETY GATE")

analytical_safety = generated_report.get(
    "analytical_safety",
    {}
)


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
            f"Missing analytical safety flag: {flag}"
        )

    value = as_bool(
        analytical_safety[flag]
    )

    print(
        f"{flag:<40}: {value}"
    )

    if value is not False:
        fail(
            f"Unsafe application state: "
            f"{flag}={value}"
        )


pass_msg(
    "All application safety flags remain False."
)


# =============================================================================
# CANDIDATE SAFETY GATE
# =============================================================================

section("CANDIDATE SAFETY GATE")

candidate_false_flags = [
    "confirmed_signal",
    "confirmed_adverse_reaction",
    "causality_established",
    "disproportionality_established",
    "incidence_established",
    "interaction_established",
]


for candidate in candidates:

    reaction = candidate["reaction"]

    for flag in candidate_false_flags:

        value = as_bool(
            candidate.get(flag)
        )

        if value is not False:
            fail(
                f"Unsafe candidate state: "
                f"{reaction} -> {flag}={value}"
            )


pass_msg(
    "All candidate analytical conclusions remain disabled."
)


# =============================================================================
# PROPOSED APPLICATION DATA MODEL
# =============================================================================

section("PROPOSED PHASE 11 APPLICATION DATA MODEL")

print(
    """
Phase 11 can generate four application-ready data objects:

1. dashboard_summary
   - total safety reports
   - Bisoprolol cases
   - candidate count
   - priority distribution
   - top candidate

2. candidate_table
   - rank
   - reaction
   - reported cases
   - percentages
   - seriousness
   - review priority
   - recommended action

3. candidate_detail_cards
   - evidence summary
   - seriousness context
   - review priority
   - follow-up recommendation
   - interpretation boundary

4. application_metadata
   - analytical limitations
   - safety restrictions
   - report version
   - decision-support scope
"""
)


# =============================================================================
# PROPOSED OUTPUT FILES
# =============================================================================

section("PROPOSED PHASE 11 OUTPUT FILES")

outputs = [
    "phase11_dashboard_summary.json",
    "phase11_candidate_table.csv",
    "phase11_candidate_cards.json",
    "phase11_application_metadata.json",
    "phase11_api_payload.json",
]


for filename in outputs:
    print(
        f"- data\\{filename}"
    )


# =============================================================================
# PHASE 11 READINESS
# =============================================================================

section("PHASE 11 READINESS")

checks = [
    (
        "Validated Phase 10 report available",
        bool(text_report)
    ),

    (
        "Machine-readable Phase 10 report available",
        bool(generated_report)
    ),

    (
        "Eight candidate records available",
        len(candidates) == 8
    ),

    (
        "Dashboard metrics available",
        len(dashboard_metrics) > 0
    ),

    (
        "Five limitations available",
        len(limitations) == 5
    ),

    (
        "No confirmed safety signal",
        analytical_safety.get(
            "confirmed_signal_established"
        ) is False
    ),

    (
        "No incidence interpretation",
        analytical_safety.get(
            "frequency_is_incidence"
        ) is False
    ),

    (
        "No causality conclusion",
        analytical_safety.get(
            "causality_established"
        ) is False
    ),

    (
        "No disproportionality conclusion",
        analytical_safety.get(
            "disproportionality_established"
        ) is False
    ),
]


ready = True

for description, result in checks:

    print(
        f"{'PASS' if result else 'FAIL'} - "
        f"{description}"
    )

    if not result:
        ready = False


if not ready:
    fail(
        "Phase 11 input readiness failed."
    )


# =============================================================================
# FINAL CONCLUSION
# =============================================================================

section("PHASE 11 INVESTIGATION CONCLUSION")

print(
    """
Phase 10 outputs are suitable for conversion into an
application-ready pharmacovigilance data package.

Phase 11 will NOT perform additional safety-signal analysis.

Its role is to transform validated Phase 10 outputs into:

- dashboard summary metrics,
- candidate data tables,
- candidate detail cards,
- frontend/API JSON payloads,
- analytical-safety metadata.

All existing analytical restrictions must remain unchanged.

Review priority remains a triage classification only.
No causal, incidence, disproportionality, confirmed-signal,
or confirmed drug-interaction conclusion may be introduced.
"""
)


header(
    "PHASE 11 INVESTIGATION COMPLETE"
)

print(
    "Next step:"
)

print(
    "analyze_phase11.py"
)