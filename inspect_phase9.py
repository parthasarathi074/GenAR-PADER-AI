import os
import pandas as pd


# =============================================================================
# PHASE 9 - FINAL PHARMACOVIGILANCE REPORT / DECISION SUPPORT INVESTIGATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_FILES = {
    "structured_reporting": "phase8_structured_reporting.csv",
    "candidate_cards": "phase8_candidate_report_cards.csv",
    "summary": "phase8_analysis_summary.csv",
}


def header(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("-" * 100)


def fail(message):
    print(f"FAIL - {message}")
    raise SystemExit(1)


# =============================================================================
# START
# =============================================================================

header("PHASE 9 - FINAL PHARMACOVIGILANCE REPORT & DECISION SUPPORT INVESTIGATION")


# =============================================================================
# FILE CHECK
# =============================================================================

section("FILE CHECK")

paths = {}

for key, filename in INPUT_FILES.items():

    file_path = os.path.join(
        DATA_DIR,
        filename
    )

    paths[key] = file_path

    if os.path.exists(file_path):
        print(f"PASS - {filename}")
    else:
        fail(
            f"Required Phase 8 file missing: {filename}"
        )


# =============================================================================
# LOAD DATA
# =============================================================================

section("LOADING PHASE 8 OUTPUTS")

reporting = pd.read_csv(
    paths["structured_reporting"]
)

cards = pd.read_csv(
    paths["candidate_cards"]
)

summary = pd.read_csv(
    paths["summary"]
)

print(
    f"Structured reporting rows : "
    f"{len(reporting):,}"
)

print(
    f"Candidate report cards    : "
    f"{len(cards):,}"
)

print(
    f"Summary rows              : "
    f"{len(summary):,}"
)


# =============================================================================
# COLUMN INVENTORY
# =============================================================================

section("STRUCTURED REPORTING COLUMN INVENTORY")

for i, column in enumerate(
    reporting.columns,
    start=1
):
    print(f"{i:02d}. {column}")


section("CANDIDATE CARD COLUMN INVENTORY")

for i, column in enumerate(
    cards.columns,
    start=1
):
    print(f"{i:02d}. {column}")


section("SUMMARY COLUMN INVENTORY")

for i, column in enumerate(
    summary.columns,
    start=1
):
    print(f"{i:02d}. {column}")


# =============================================================================
# REQUIRED COLUMN VALIDATION
# =============================================================================

section("REQUIRED COLUMN VALIDATION")

required_reporting = [
    "reactionmeddrapt",
    "reported_cases",
    "percentage_of_all_cases",
    "serious_cases",
    "serious_percentage",
    "death_cases",
    "hospitalization_cases",
    "mean_age",
    "median_age",
    "evidence_level",
    "analysis_type",
    "frequency_interpretation",
    "causality_status",
    "disproportionality_status",
    "comparator_status",
    "interaction_status",
]

required_cards = [
    "rank",
    "reaction",
    "reported_cases",
    "percentage_of_all_cases",
    "serious_cases",
    "serious_percentage",
    "death_cases",
    "hospitalization_cases",
    "evidence_level",
    "frequency_interpretation",
    "causality",
    "disproportionality",
    "comparator",
    "interaction",
]

required_summary = [
    "integrated_cases",
    "bisoprolol_cases",
    "candidate_reactions",
    "candidate_case_reaction_rows",
    "candidate_unique_cases",
    "unique_raw_reaction_terms",
    "top_candidate",
    "top_candidate_cases",
    "top_candidate_percentage",
    "top_candidate_serious_cases",
    "comparator_available",
    "ror_available",
    "prr_available",
    "frequency_is_incidence",
    "causality_established",
    "disproportionality_established",
    "co_medication_interaction_established",
    "analysis_type",
    "reporting_scope",
    "interpretation",
    "major_limitation",
]


for column in required_reporting:

    if column not in reporting.columns:
        fail(
            f"Missing reporting column: {column}"
        )

    print(
        f"PASS - reporting: {column}"
    )


for column in required_cards:

    if column not in cards.columns:
        fail(
            f"Missing candidate-card column: {column}"
        )

    print(
        f"PASS - cards: {column}"
    )


for column in required_summary:

    if column not in summary.columns:
        fail(
            f"Missing summary column: {column}"
        )

    print(
        f"PASS - summary: {column}"
    )


# =============================================================================
# CANDIDATE INVENTORY
# =============================================================================

section("CANDIDATE INVENTORY")

cards_sorted = cards.sort_values(
    by="rank"
)

for _, row in cards_sorted.iterrows():

    print(
        f"{int(row['rank']):02d}. "
        f"{row['reaction']} | "
        f"cases={int(row['reported_cases'])} | "
        f"serious={int(row['serious_cases'])} | "
        f"serious%="
        f"{float(row['serious_percentage']):.2f}% | "
        f"evidence={row['evidence_level']}"
    )


# =============================================================================
# PRIORITY INPUT STRUCTURE
# =============================================================================

section("PRIORITY INPUT STRUCTURE")

print(
    "Phase 9 will prioritize candidates using "
    "descriptive evidence only."
)

print()

print(
    "Available decision-support inputs:"
)

print(
    "1. Reported case frequency"
)

print(
    "2. Serious-case count"
)

print(
    "3. Serious-case percentage"
)

print(
    "4. Death-case count"
)

print(
    "5. Hospitalization-case count"
)

print(
    "6. Evidence-level classification"
)

print(
    "7. Candidate ranking"
)

print()

print(
    "Unavailable statistical evidence:"
)

print(
    "- Reporting Odds Ratio (ROR)"
)

print(
    "- Proportional Reporting Ratio (PRR)"
)

print(
    "- Internal exposure comparator"
)

print(
    "- Incidence estimates"
)

print(
    "- Causal attribution"
)


# =============================================================================
# TOP CANDIDATE CHECK
# =============================================================================

section("TOP CANDIDATE INVESTIGATION")

if cards_sorted.empty:
    fail(
        "Candidate card dataset is empty."
    )

top = cards_sorted.iloc[0]

print(
    f"Reaction            : "
    f"{top['reaction']}"
)

print(
    f"Reported cases      : "
    f"{int(top['reported_cases'])}"
)

print(
    f"Percentage of cases : "
    f"{float(top['percentage_of_all_cases']):.2f}%"
)

print(
    f"Serious cases       : "
    f"{int(top['serious_cases'])}"
)

print(
    f"Serious percentage  : "
    f"{float(top['serious_percentage']):.2f}%"
)

print(
    f"Death cases         : "
    f"{int(top['death_cases'])}"
)

print(
    f"Hospitalizations    : "
    f"{int(top['hospitalization_cases'])}"
)

print(
    f"Evidence level      : "
    f"{top['evidence_level']}"
)


# =============================================================================
# SAFETY FLAGS
# =============================================================================

section("ANALYTICAL SAFETY FLAGS")

if len(summary) != 1:
    fail(
        "Expected exactly one Phase 8 summary row."
    )

summary_row = summary.iloc[0]

flags = {
    "Comparator available":
        summary_row[
            "comparator_available"
        ],

    "ROR available":
        summary_row[
            "ror_available"
        ],

    "PRR available":
        summary_row[
            "prr_available"
        ],

    "Frequency is incidence":
        summary_row[
            "frequency_is_incidence"
        ],

    "Causality established":
        summary_row[
            "causality_established"
        ],

    "Disproportionality established":
        summary_row[
            "disproportionality_established"
        ],

    "Co-medication interaction established":
        summary_row[
            "co_medication_interaction_established"
        ],
}

for name, value in flags.items():
    print(
        f"{name:<42}: {value}"
    )


# =============================================================================
# SUMMARY COUNTS
# =============================================================================

section("PHASE 8 SUMMARY COUNTS")

print(
    f"Integrated cases       : "
    f"{int(summary_row['integrated_cases']):,}"
)

print(
    f"Bisoprolol cases       : "
    f"{int(summary_row['bisoprolol_cases']):,}"
)

print(
    f"Candidate reactions    : "
    f"{int(summary_row['candidate_reactions']):,}"
)

print(
    f"Candidate case rows    : "
    f"{int(summary_row['candidate_case_reaction_rows']):,}"
)

print(
    f"Candidate unique cases : "
    f"{int(summary_row['candidate_unique_cases']):,}"
)

print(
    f"Unique reaction terms  : "
    f"{int(summary_row['unique_raw_reaction_terms']):,}"
)


# =============================================================================
# DATA QUALITY CHECKS
# =============================================================================

section("DECISION-SUPPORT DATA QUALITY")

if reporting["reactionmeddrapt"].duplicated().any():
    fail(
        "Duplicate reactions detected in structured reporting."
    )

print(
    "PASS - Reporting candidates are unique."
)


if cards["reaction"].duplicated().any():
    fail(
        "Duplicate reactions detected in candidate cards."
    )

print(
    "PASS - Candidate-card reactions are unique."
)


if len(reporting) != len(cards):
    fail(
        "Reporting/card candidate counts do not match."
    )

print(
    "PASS - Reporting and card counts match."
)


reporting_candidates = set(
    reporting["reactionmeddrapt"]
    .astype(str)
    .str.strip()
)

card_candidates = set(
    cards["reaction"]
    .astype(str)
    .str.strip()
)

if reporting_candidates != card_candidates:
    fail(
        "Reporting/card reaction sets do not match."
    )

print(
    "PASS - Candidate reaction sets match."
)


# =============================================================================
# DECISION-SUPPORT READINESS
# =============================================================================

section("PHASE 9 DECISION-SUPPORT READINESS")

checks = [
    (
        "Candidate ranking available",
        len(cards) > 0
    ),
    (
        "Reported frequency available",
        "reported_cases" in cards.columns
    ),
    (
        "Seriousness evidence available",
        "serious_cases" in cards.columns
    ),
    (
        "Death-case evidence available",
        "death_cases" in cards.columns
    ),
    (
        "Hospitalization evidence available",
        "hospitalization_cases"
        in cards.columns
    ),
    (
        "Evidence levels available",
        "evidence_level" in cards.columns
    ),
    (
        "Analytical limitations documented",
        "major_limitation"
        in summary.columns
    ),
]

for description, result in checks:

    print(
        f"{'PASS' if result else 'FAIL'} - "
        f"{description}"
    )


# =============================================================================
# PHASE 9 CONCLUSION
# =============================================================================

section("PHASE 9 INVESTIGATION CONCLUSION")

print(
    """
The validated Phase 8 reporting layer is ready for
Phase 9 final pharmacovigilance decision-support analysis.

Phase 9 can safely produce:

1. Candidate priority categories
2. Candidate evidence summaries
3. Seriousness-focused assessments
4. Candidate follow-up recommendations
5. Analytical limitation statements
6. A final machine-readable safety assessment

Priority categories will represent review priority only.

They MUST NOT be interpreted as:

- confirmed safety signals,
- causal adverse reactions,
- incidence estimates,
- disproportionality findings,
- confirmed drug-drug interactions.

No ROR or PRR will be calculated because the current dataset
contains no internal non-Bisoprolol comparator cohort.
"""
)


print("=" * 100)
print("PHASE 9 INVESTIGATION COMPLETE")
print("=" * 100)