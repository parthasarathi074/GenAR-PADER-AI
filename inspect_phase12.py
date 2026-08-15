import os
import json
import pandas as pd


# =============================================================================
# PHASE 12 - FINAL END-TO-END PIPELINE INVESTIGATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


REQUIRED_FILES = [
    # Phase 1
    "normalized_drugs.csv",
    "drug_alignment_report.csv",

    # Phase 2
    "normalized_reactions.csv",
    "reaction_alignment_report.csv",

    # Phase 4
    "integrated_icsr_cases.csv",

    # Phase 5
    "phase5_case_cohort.csv",
    "phase5_case_reactions.csv",
    "phase5_signal_candidates.csv",
    "phase5_signal_summary.csv",

    # Phase 6
    "phase6_candidate_profiles.csv",
    "phase6_candidate_demographics.csv",
    "phase6_candidate_countries.csv",
    "phase6_candidate_products.csv",
    "phase6_analysis_summary.csv",

    # Phase 7
    "phase7_candidate_evidence.csv",
    "phase7_candidate_ranking.csv",
    "phase7_candidate_seriousness.csv",
    "phase7_candidate_demographics.csv",
    "phase7_candidate_countries.csv",
    "phase7_candidate_products.csv",
    "phase7_reporting_matrix.csv",
    "phase7_analysis_summary.csv",

    # Phase 8
    "phase8_structured_reporting.csv",
    "phase8_candidate_report_cards.csv",
    "phase8_analysis_summary.csv",

    # Phase 9
    "phase9_signal_assessment.csv",
    "phase9_candidate_summaries.csv",
    "phase9_safety_assessment.csv",
    "phase9_limitation_assessment.csv",
    "phase9_decision_support.csv",
    "phase9_analysis_summary.csv",

    # Phase 10
    "phase10_genai_context.json",
    "phase10_candidate_context.json",
    "phase10_reporting_rules.json",
    "phase10_pharmacovigilance_report.txt",
    "phase10_generated_report.json",

    # Phase 11
    "phase11_dashboard_summary.json",
    "phase11_candidate_table.csv",
    "phase11_candidate_cards.json",
    "phase11_application_metadata.json",
    "phase11_api_payload.json",
]


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
    raise SystemExit(1)


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        fail(
            f"Unable to load {os.path.basename(path)}: {exc}"
        )


# =============================================================================
# START
# =============================================================================

section(
    "PHASE 12 - FINAL END-TO-END PIPELINE INVESTIGATION"
)


# =============================================================================
# FILE INVENTORY
# =============================================================================

section("REQUIRED FILE INVENTORY")

missing_files = []
empty_files = []

for filename in REQUIRED_FILES:

    path = os.path.join(
        DATA_DIR,
        filename
    )

    if not os.path.exists(path):
        missing_files.append(
            filename
        )
        print(
            f"FAIL - Missing: {filename}"
        )
        continue

    size = os.path.getsize(path)

    if size == 0:
        empty_files.append(
            filename
        )
        print(
            f"FAIL - Empty: {filename}"
        )
        continue

    print(
        f"PASS - {filename:<45} "
        f"{size:>10,} bytes"
    )


if missing_files:
    fail(
        f"{len(missing_files)} required files missing."
    )


if empty_files:
    fail(
        f"{len(empty_files)} required files empty."
    )


pass_msg(
    f"All {len(REQUIRED_FILES)} required pipeline files exist."
)


# =============================================================================
# CORE DATASET LOAD
# =============================================================================

section("CORE DATASET VALIDATION")

drugs = pd.read_csv(
    os.path.join(
        DATA_DIR,
        "normalized_drugs.csv"
    )
)

reactions = pd.read_csv(
    os.path.join(
        DATA_DIR,
        "normalized_reactions.csv"
    )
)

integrated = pd.read_csv(
    os.path.join(
        DATA_DIR,
        "integrated_icsr_cases.csv"
    )
)


print(
    f"Normalized drug rows     : {len(drugs):,}"
)

print(
    f"Normalized reaction rows : {len(reactions):,}"
)

print(
    f"Integrated case rows     : {len(integrated):,}"
)


if len(drugs) != 10444:
    fail(
        f"Unexpected normalized drug row count: {len(drugs):,}"
    )

pass_msg(
    "Normalized drug row count: 10,444"
)


if len(reactions) != 3423:
    fail(
        f"Unexpected normalized reaction row count: {len(reactions):,}"
    )

pass_msg(
    "Normalized reaction row count: 3,423"
)


if len(integrated) != 1024:
    fail(
        f"Unexpected integrated case count: {len(integrated):,}"
    )

pass_msg(
    "Integrated case count: 1,024"
)


# =============================================================================
# CASE COVERAGE
# =============================================================================

section("CASE COVERAGE")

drug_cases = drugs[
    "safetyreportid"
].nunique()

reaction_cases = reactions[
    "safetyreportid"
].nunique()

integrated_cases = integrated[
    "safetyreportid"
].nunique()


print(
    f"Drug cases       : {drug_cases:,}"
)

print(
    f"Reaction cases   : {reaction_cases:,}"
)

print(
    f"Integrated cases : {integrated_cases:,}"
)


if drug_cases != 1024:
    fail(
        "Drug case coverage mismatch."
    )

if reaction_cases != 1024:
    fail(
        "Reaction case coverage mismatch."
    )

if integrated_cases != 1024:
    fail(
        "Integrated case coverage mismatch."
    )


pass_msg(
    "All core datasets represent 1,024 cases."
)


# =============================================================================
# PHASE 11 FINAL APPLICATION LOAD
# =============================================================================

section("PHASE 11 APPLICATION VALIDATION")

dashboard = load_json(
    os.path.join(
        DATA_DIR,
        "phase11_dashboard_summary.json"
    )
)

metadata = load_json(
    os.path.join(
        DATA_DIR,
        "phase11_application_metadata.json"
    )
)

api_payload = load_json(
    os.path.join(
        DATA_DIR,
        "phase11_api_payload.json"
    )
)

candidate_table = pd.read_csv(
    os.path.join(
        DATA_DIR,
        "phase11_candidate_table.csv"
    )
)


print(
    f"Dashboard total reports : "
    f"{dashboard.get('total_safety_reports')}"
)

print(
    f"Dashboard candidates    : "
    f"{dashboard.get('candidate_reactions')}"
)

print(
    f"Candidate table rows    : "
    f"{len(candidate_table)}"
)


if dashboard.get(
    "total_safety_reports"
) != 1024:
    fail(
        "Dashboard total report count mismatch."
    )


if dashboard.get(
    "candidate_reactions"
) != 8:
    fail(
        "Dashboard candidate count mismatch."
    )


if len(candidate_table) != 8:
    fail(
        "Candidate table row count mismatch."
    )


pass_msg(
    "Phase 11 application counts are consistent."
)


# =============================================================================
# TOP CANDIDATE
# =============================================================================

section("FINAL TOP CANDIDATE CHECK")

top = dashboard.get(
    "top_candidate",
    {}
)


print(
    f"Reaction       : {top.get('reaction')}"
)

print(
    f"Reported cases : {top.get('reported_cases')}"
)

print(
    f"Priority       : {top.get('priority')}"
)


if top.get(
    "reaction"
) != "Acute kidney injury":
    fail(
        "Unexpected top candidate."
    )


if top.get(
    "reported_cases"
) != 22:
    fail(
        "Unexpected top candidate case count."
    )


if top.get(
    "priority"
) != "higher_priority_candidate":
    fail(
        "Unexpected top candidate priority."
    )


pass_msg(
    "Top candidate remains Acute kidney injury."
)


# =============================================================================
# PRIORITY DISTRIBUTION
# =============================================================================

section("FINAL PRIORITY DISTRIBUTION")

priority_distribution = dashboard.get(
    "priority_distribution",
    {}
)


expected_priority_distribution = {
    "higher_priority_candidate": 1,
    "moderate_priority_candidate": 2,
    "lower_priority_candidate": 5,
}


for priority, expected in (
    expected_priority_distribution.items()
):

    actual = priority_distribution.get(
        priority
    )

    print(
        f"{priority:<35}: {actual}"
    )

    if actual != expected:
        fail(
            f"{priority} count mismatch."
        )


pass_msg(
    "Final priority distribution is valid."
)


# =============================================================================
# FINAL SAFETY VALIDATION
# =============================================================================

section("FINAL ANALYTICAL SAFETY VALIDATION")

restrictions = metadata.get(
    "analytical_restrictions",
    {}
)


false_flags = [
    "comparator_available",
    "ror_available",
    "prr_available",
    "frequency_is_incidence",
    "causality_established",
    "disproportionality_established",
    "confirmed_signal_established",
    "drug_interaction_established",
]


for flag in false_flags:

    value = restrictions.get(
        flag
    )

    print(
        f"{flag:<40}: {value}"
    )

    if value is not False:
        fail(
            f"Analytical safety violation: {flag}"
        )


pass_msg(
    "All final analytical safety restrictions remain active."
)


# =============================================================================
# FRONTEND SAFETY
# =============================================================================

section("FINAL FRONTEND SAFETY VALIDATION")

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

    value = display.get(
        flag
    )

    print(
        f"{flag:<35}: {value}"
    )

    if value is not False:
        fail(
            f"Unsafe frontend option enabled: {flag}"
        )


pass_msg(
    "Unsafe analytical display options remain disabled."
)


# =============================================================================
# FINAL PIPELINE STATUS
# =============================================================================

section("PIPELINE STATUS")

phase_status = {
    1: "Drug normalization",
    2: "Reaction normalization",
    3: "Structure validation",
    4: "Case integration",
    5: "Pharmacovigilance screen",
    6: "Signal pattern analysis",
    7: "Evidence & reporting",
    8: "Structured reporting",
    9: "Decision support",
    10: "Controlled reporting",
    11: "Application output",
}


for phase, description in (
    phase_status.items()
):

    print(
        f"Phase {phase:<2} - "
        f"{description:<35}: COMPLETE"
    )


# =============================================================================
# RELEASE READINESS
# =============================================================================

section("PHASE 12 RELEASE READINESS")

release_checks = [
    (
        "All expected pipeline files exist",
        True
    ),
    (
        "Drug normalization dataset valid",
        len(drugs) == 10444
    ),
    (
        "Reaction normalization dataset valid",
        len(reactions) == 3423
    ),
    (
        "Integrated case dataset valid",
        len(integrated) == 1024
    ),
    (
        "Application candidate table valid",
        len(candidate_table) == 8
    ),
    (
        "Final comparator unavailable",
        restrictions.get(
            "comparator_available"
        ) is False
    ),
    (
        "Final ROR unavailable",
        restrictions.get(
            "ror_available"
        ) is False
    ),
    (
        "Final PRR unavailable",
        restrictions.get(
            "prr_available"
        ) is False
    ),
    (
        "Final incidence interpretation disabled",
        restrictions.get(
            "frequency_is_incidence"
        ) is False
    ),
    (
        "Final causality disabled",
        restrictions.get(
            "causality_established"
        ) is False
    ),
    (
        "Final confirmed-signal status disabled",
        restrictions.get(
            "confirmed_signal_established"
        ) is False
    ),
]


ready = True

for description, status in release_checks:

    print(
        f"{'PASS' if status else 'FAIL'} - "
        f"{description}"
    )

    if not status:
        ready = False


if not ready:
    fail(
        "Final release readiness failed."
    )


# =============================================================================
# FINAL CONCLUSION
# =============================================================================

section("PHASE 12 INVESTIGATION CONCLUSION")

print(
    """
The complete GenAR-PADER-AI analytical pipeline is ready
for final release packaging.

Validated pipeline scope:

- raw ICSR ingestion
- latest-version case selection
- drug normalization
- reaction normalization
- integrated case construction
- descriptive pharmacovigilance screening
- candidate pattern analysis
- evidence reporting
- review-priority decision support
- controlled human-readable reporting
- frontend/API application outputs

Final analytical restrictions remain active:

- no internal non-Bisoprolol comparator
- no ROR
- no PRR
- no incidence interpretation
- no causal conclusion
- no confirmed disproportionality
- no confirmed safety signal
- no confirmed drug-drug interaction

The next step is to build the final Phase 12 release manifest
and release package metadata.
"""
)


section(
    "PHASE 12 INVESTIGATION COMPLETE"
)

print(
    "Next step:"
)

print(
    "build_phase12_release.py"
)