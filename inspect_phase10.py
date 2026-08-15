import os
import sys
import pandas as pd


# =============================================================================
# PHASE 10 - GENAI REPORT GENERATION INVESTIGATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_FILES = {
    "signal_assessment": "phase9_signal_assessment.csv",
    "candidate_summaries": "phase9_candidate_summaries.csv",
    "safety_assessment": "phase9_safety_assessment.csv",
    "limitations": "phase9_limitation_assessment.csv",
    "decision_support": "phase9_decision_support.csv",
    "summary": "phase9_analysis_summary.csv",
}


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


def to_bool(value):
    if isinstance(value, bool):
        return value

    if pd.isna(value):
        return False

    text = str(value).strip().lower()

    if text in {"true", "1", "yes", "y"}:
        return True

    if text in {"false", "0", "no", "n"}:
        return False

    fail(f"Unable to interpret boolean value: {value}")


# =============================================================================
# START
# =============================================================================

header(
    "PHASE 10 - GENAI PHARMACOVIGILANCE REPORT GENERATION INVESTIGATION"
)


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

    if not os.path.exists(file_path):
        fail(
            f"Required Phase 9 file missing: {filename}"
        )

    print(f"PASS - {filename}")


# =============================================================================
# LOAD PHASE 9 OUTPUTS
# =============================================================================

section("LOADING PHASE 9 OUTPUTS")

signal_assessment = pd.read_csv(
    paths["signal_assessment"]
)

candidate_summaries = pd.read_csv(
    paths["candidate_summaries"]
)

safety_assessment = pd.read_csv(
    paths["safety_assessment"]
)

limitations = pd.read_csv(
    paths["limitations"]
)

decision_support = pd.read_csv(
    paths["decision_support"]
)

summary = pd.read_csv(
    paths["summary"]
)


print(
    f"Signal assessment rows  : "
    f"{len(signal_assessment):,}"
)

print(
    f"Candidate summary rows  : "
    f"{len(candidate_summaries):,}"
)

print(
    f"Safety assessment rows  : "
    f"{len(safety_assessment):,}"
)

print(
    f"Limitation rows         : "
    f"{len(limitations):,}"
)

print(
    f"Decision-support rows   : "
    f"{len(decision_support):,}"
)

print(
    f"Summary rows            : "
    f"{len(summary):,}"
)


# =============================================================================
# COLUMN INVENTORY
# =============================================================================

datasets = {
    "SIGNAL ASSESSMENT": signal_assessment,
    "CANDIDATE SUMMARIES": candidate_summaries,
    "SAFETY ASSESSMENT": safety_assessment,
    "LIMITATIONS": limitations,
    "DECISION SUPPORT": decision_support,
    "SUMMARY": summary,
}


for name, df in datasets.items():

    section(f"{name} COLUMN INVENTORY")

    for index, column in enumerate(
        df.columns,
        start=1
    ):
        print(
            f"{index:02d}. {column}"
        )


# =============================================================================
# REQUIRED COLUMN VALIDATION
# =============================================================================

section("REQUIRED COLUMN VALIDATION")


required_signal_columns = [
    "rank",
    "reactionmeddrapt",
    "reported_cases",
    "percentage_of_all_cases",
    "serious_cases",
    "serious_percentage",
    "death_cases",
    "hospitalization_cases",
    "evidence_level",
    "review_priority",
    "confirmed_signal",
    "causality_established",
    "disproportionality_established",
    "incidence_established",
    "interaction_established",
    "analysis_type",
]


required_summary_columns = [
    "rank",
    "reactionmeddrapt",
    "reported_cases",
    "percentage_of_all_cases",
    "serious_cases",
    "serious_percentage",
    "death_cases",
    "hospitalization_cases",
    "evidence_level",
    "review_priority",
    "evidence_summary",
    "follow_up_recommendation",
    "interpretation_scope",
]


required_decision_columns = [
    "rank",
    "reactionmeddrapt",
    "reported_cases",
    "percentage_of_all_cases",
    "serious_cases",
    "serious_percentage",
    "death_cases",
    "hospitalization_cases",
    "evidence_level",
    "review_priority",
    "recommended_action",
    "confirmed_signal",
    "frequency_is_incidence",
    "causality_established",
    "comparator_available",
    "ror_available",
    "prr_available",
    "disproportionality_established",
    "interaction_established",
    "decision_scope",
]


required_phase_summary_columns = [
    "integrated_cases",
    "bisoprolol_cases",
    "candidate_reactions",
    "higher_priority_candidates",
    "moderate_priority_candidates",
    "lower_priority_candidates",
    "top_candidate",
    "top_candidate_cases",
    "top_candidate_priority",
    "comparator_available",
    "ror_available",
    "prr_available",
    "frequency_is_incidence",
    "causality_established",
    "disproportionality_established",
    "co_medication_interaction_established",
    "confirmed_signal_established",
    "analysis_type",
    "decision_scope",
    "major_limitation",
    "interpretation",
]


def validate_columns(
    dataframe,
    required_columns,
    dataset_name
):
    for column in required_columns:

        if column not in dataframe.columns:
            fail(
                f"Missing column '{column}' "
                f"in {dataset_name}"
            )

        print(
            f"PASS - {dataset_name}: {column}"
        )


validate_columns(
    signal_assessment,
    required_signal_columns,
    "signal_assessment"
)

validate_columns(
    candidate_summaries,
    required_summary_columns,
    "candidate_summaries"
)

validate_columns(
    decision_support,
    required_decision_columns,
    "decision_support"
)

validate_columns(
    summary,
    required_phase_summary_columns,
    "summary"
)


# =============================================================================
# SUMMARY STRUCTURE
# =============================================================================

section("PHASE 9 SUMMARY STRUCTURE")

if len(summary) != 1:
    fail(
        "Phase 9 summary must contain exactly one row."
    )

summary_row = summary.iloc[0]


print(
    f"Integrated cases    : "
    f"{int(float(summary_row['integrated_cases'])):,}"
)

print(
    f"Bisoprolol cases    : "
    f"{int(float(summary_row['bisoprolol_cases'])):,}"
)

print(
    f"Candidate reactions : "
    f"{int(float(summary_row['candidate_reactions']))}"
)

print(
    f"Higher priority     : "
    f"{int(float(summary_row['higher_priority_candidates']))}"
)

print(
    f"Moderate priority   : "
    f"{int(float(summary_row['moderate_priority_candidates']))}"
)

print(
    f"Lower priority      : "
    f"{int(float(summary_row['lower_priority_candidates']))}"
)

print(
    f"Top candidate       : "
    f"{summary_row['top_candidate']}"
)

print(
    f"Top candidate cases : "
    f"{int(float(summary_row['top_candidate_cases']))}"
)

print(
    f"Top priority        : "
    f"{summary_row['top_candidate_priority']}"
)


# =============================================================================
# CANDIDATE REPORT CONTENT CHECK
# =============================================================================

section("CANDIDATE REPORT CONTENT")

sorted_candidates = candidate_summaries.sort_values(
    by="rank"
)

for _, row in sorted_candidates.iterrows():

    print()
    print(
        f"Rank {int(row['rank'])}: "
        f"{row['reactionmeddrapt']}"
    )

    print(
        f"  Reported cases     : "
        f"{int(row['reported_cases'])}"
    )

    print(
        f"  Percentage         : "
        f"{float(row['percentage_of_all_cases']):.2f}%"
    )

    print(
        f"  Serious cases      : "
        f"{int(row['serious_cases'])}"
    )

    print(
        f"  Death cases        : "
        f"{int(row['death_cases'])}"
    )

    print(
        f"  Hospitalizations   : "
        f"{int(row['hospitalization_cases'])}"
    )

    print(
        f"  Review priority    : "
        f"{row['review_priority']}"
    )

    print(
        f"  Follow-up          : "
        f"{row['follow_up_recommendation']}"
    )


# =============================================================================
# LIMITATION CONTENT
# =============================================================================

section("ANALYTICAL LIMITATIONS")

for _, row in limitations.iterrows():

    print()
    print(
        f"Limitation {int(row['limitation_id'])}"
    )

    print(
        f"  Issue       : "
        f"{row['limitation']}"
    )

    print(
        f"  Impact      : "
        f"{row['impact']}"
    )

    print(
        f"  Restriction : "
        f"{row['restriction']}"
    )


# =============================================================================
# GENAI SAFETY GATE
# =============================================================================

section("GENAI SAFETY GATE")


safety_flags = {
    "Comparator available":
        to_bool(
            summary_row[
                "comparator_available"
            ]
        ),

    "ROR available":
        to_bool(
            summary_row[
                "ror_available"
            ]
        ),

    "PRR available":
        to_bool(
            summary_row[
                "prr_available"
            ]
        ),

    "Frequency interpreted as incidence":
        to_bool(
            summary_row[
                "frequency_is_incidence"
            ]
        ),

    "Causality established":
        to_bool(
            summary_row[
                "causality_established"
            ]
        ),

    "Disproportionality established":
        to_bool(
            summary_row[
                "disproportionality_established"
            ]
        ),

    "Interaction established":
        to_bool(
            summary_row[
                "co_medication_interaction_established"
            ]
        ),

    "Confirmed signal established":
        to_bool(
            summary_row[
                "confirmed_signal_established"
            ]
        ),
}


for label, value in safety_flags.items():

    print(
        f"{label:<42}: {value}"
    )

    if value:
        fail(
            f"Unsafe Phase 10 input state: "
            f"{label} is True."
        )


print()
print(
    "PASS - All prohibited analytical claims "
    "remain disabled."
)


# =============================================================================
# GENAI REPORTING RULES
# =============================================================================

section("GENAI REPORTING RULES")

rules = [
    "Use only validated Phase 9 values.",
    "Do not change or invent numerical values.",
    "Do not interpret reporting frequency as incidence.",
    "Do not claim a causal relationship.",
    "Do not claim a confirmed safety signal.",
    "Do not calculate or infer ROR or PRR.",
    "Do not claim disproportionality.",
    "Do not claim confirmed drug-drug interactions.",
    "Clearly describe review priorities as triage categories only.",
    "Always include analytical limitations.",
]

for i, rule in enumerate(
    rules,
    start=1
):
    print(
        f"{i:02d}. {rule}"
    )


# =============================================================================
# REPORT SECTIONS
# =============================================================================

section("PROPOSED GENAI REPORT STRUCTURE")

report_sections = [
    "Executive Summary",
    "Dataset Overview",
    "Methodology Overview",
    "Candidate Review Priority Summary",
    "Candidate-by-Candidate Evidence",
    "Seriousness Assessment",
    "Recommended Follow-up Actions",
    "Analytical Limitations",
    "Interpretation Boundaries",
    "Final Pharmacovigilance Summary",
]

for index, report_section in enumerate(
    report_sections,
    start=1
):
    print(
        f"{index:02d}. {report_section}"
    )


# =============================================================================
# PHASE 10 READINESS
# =============================================================================

section("PHASE 10 READINESS")

checks = [
    (
        "Signal assessment available",
        len(signal_assessment) > 0
    ),

    (
        "Candidate summaries available",
        len(candidate_summaries) > 0
    ),

    (
        "Safety assessment available",
        len(safety_assessment) > 0
    ),

    (
        "Analytical limitations available",
        len(limitations) > 0
    ),

    (
        "Decision support available",
        len(decision_support) > 0
    ),

    (
        "Summary available",
        len(summary) == 1
    ),

    (
        "Eight candidate reactions available",
        len(candidate_summaries) == 8
    ),

    (
        "No confirmed safety signal",
        not to_bool(
            summary_row[
                "confirmed_signal_established"
            ]
        )
    ),

    (
        "No causal conclusion",
        not to_bool(
            summary_row[
                "causality_established"
            ]
        )
    ),

    (
        "No disproportionality conclusion",
        not to_bool(
            summary_row[
                "disproportionality_established"
            ]
        )
    ),
]


for description, result in checks:

    print(
        f"{'PASS' if result else 'FAIL'} - "
        f"{description}"
    )


# =============================================================================
# FINAL CONCLUSION
# =============================================================================

section("PHASE 10 INVESTIGATION CONCLUSION")

print(
    """
The validated Phase 9 outputs are suitable for a controlled
GenAI pharmacovigilance reporting layer.

The GenAI component should NOT perform the primary analysis.

Its role should be limited to:

1. Converting validated structured values into readable text.
2. Producing candidate-by-candidate summaries.
3. Explaining review-priority classifications.
4. Summarizing seriousness evidence.
5. Presenting recommended follow-up actions.
6. Explaining analytical limitations.
7. Producing a human-readable final safety report.

The GenAI layer must not:

- invent case counts,
- change percentages,
- infer incidence,
- infer causality,
- infer disproportionality,
- calculate ROR/PRR,
- establish drug-drug interactions,
- convert a review-priority candidate into a confirmed signal.

The next step is to create a controlled machine-readable
GenAI context file from the validated Phase 9 outputs.
"""
)


header("PHASE 10 INVESTIGATION COMPLETE")