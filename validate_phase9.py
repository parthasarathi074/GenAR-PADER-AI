import os
import sys
import pandas as pd


# =============================================================================
# PHASE 9 - FINAL PHARMACOVIGILANCE DECISION SUPPORT VALIDATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


FILES = {
    "signal_assessment": "phase9_signal_assessment.csv",
    "candidate_summaries": "phase9_candidate_summaries.csv",
    "safety_assessment": "phase9_safety_assessment.csv",
    "limitations": "phase9_limitation_assessment.csv",
    "decision_support": "phase9_decision_support.csv",
    "summary": "phase9_analysis_summary.csv",
}


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


def require_columns(df, required, label):
    for column in required:
        if column not in df.columns:
            fail(
                f"Missing required column "
                f"'{column}' in {label}"
            )

        pass_msg(f"{label}: {column}")


# =============================================================================
# START
# =============================================================================

section(
    "PHASE 9 - FINAL PHARMACOVIGILANCE "
    "DECISION SUPPORT VALIDATION"
)


# =============================================================================
# FILE CHECK
# =============================================================================

section("FILE CHECK")

paths = {}

for key, filename in FILES.items():

    file_path = os.path.join(
        DATA_DIR,
        filename
    )

    paths[key] = file_path

    if not os.path.exists(file_path):
        fail(
            f"Required Phase 9 file missing: "
            f"{filename}"
        )

    pass_msg(filename)


# =============================================================================
# LOAD DATASETS
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
# COLUMN VALIDATION
# =============================================================================

section("COLUMN VALIDATION")


required_signal = [
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


required_candidate_summary = [
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


required_safety = [
    "reactionmeddrapt",
    "review_priority",
    "reported_cases",
    "serious_cases",
    "death_cases",
    "hospitalization_cases",
    "requires_case_review",
    "confirmed_adverse_reaction",
    "confirmed_signal",
    "causal_relationship",
    "disproportionality_status",
    "incidence_status",
    "interaction_status",
]


required_limitations = [
    "limitation_id",
    "limitation",
    "impact",
    "restriction",
]


required_decision = [
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


required_summary = [
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


require_columns(
    signal_assessment,
    required_signal,
    "signal_assessment"
)

require_columns(
    candidate_summaries,
    required_candidate_summary,
    "candidate_summaries"
)

require_columns(
    safety_assessment,
    required_safety,
    "safety_assessment"
)

require_columns(
    limitations,
    required_limitations,
    "limitations"
)

require_columns(
    decision_support,
    required_decision,
    "decision_support"
)

require_columns(
    summary,
    required_summary,
    "summary"
)


# =============================================================================
# ROW COUNT VALIDATION
# =============================================================================

section("ROW COUNT VALIDATION")

expected_candidates = 8

candidate_datasets = {
    "signal assessment":
        signal_assessment,

    "candidate summaries":
        candidate_summaries,

    "safety assessment":
        safety_assessment,

    "decision support":
        decision_support,
}


for label, df in candidate_datasets.items():

    if len(df) != expected_candidates:
        fail(
            f"Expected {expected_candidates} rows "
            f"in {label}, found {len(df)}"
        )

    pass_msg(
        f"{label}: {expected_candidates} candidates"
    )


if len(limitations) != 5:
    fail(
        f"Expected 5 analytical limitations, "
        f"found {len(limitations)}"
    )

pass_msg(
    "Five analytical limitations present."
)


if len(summary) != 1:
    fail(
        f"Expected exactly one Phase 9 summary row, "
        f"found {len(summary)}"
    )

pass_msg(
    "One Phase 9 summary row present."
)


# =============================================================================
# CANDIDATE CONSISTENCY
# =============================================================================

section("CANDIDATE CONSISTENCY VALIDATION")

signal_candidates = set(
    signal_assessment[
        "reactionmeddrapt"
    ].astype(str).str.strip()
)

summary_candidates = set(
    candidate_summaries[
        "reactionmeddrapt"
    ].astype(str).str.strip()
)

safety_candidates = set(
    safety_assessment[
        "reactionmeddrapt"
    ].astype(str).str.strip()
)

decision_candidates = set(
    decision_support[
        "reactionmeddrapt"
    ].astype(str).str.strip()
)


if signal_candidates != summary_candidates:
    fail(
        "Signal assessment and candidate "
        "summary reactions do not match."
    )

pass_msg(
    "Signal assessment and candidate summaries match."
)


if signal_candidates != safety_candidates:
    fail(
        "Signal assessment and safety "
        "assessment reactions do not match."
    )

pass_msg(
    "Signal assessment and safety assessment match."
)


if signal_candidates != decision_candidates:
    fail(
        "Signal assessment and decision-support "
        "reactions do not match."
    )

pass_msg(
    "Signal assessment and decision support match."
)


# =============================================================================
# RANK VALIDATION
# =============================================================================

section("RANK VALIDATION")

ranks = pd.to_numeric(
    decision_support["rank"],
    errors="coerce"
)

if ranks.isna().any():
    fail(
        "Decision-support ranking contains "
        "non-numeric values."
    )

actual_ranks = sorted(
    ranks.astype(int).tolist()
)

expected_ranks = list(
    range(
        1,
        expected_candidates + 1
    )
)

if actual_ranks != expected_ranks:
    fail(
        f"Invalid ranking sequence. "
        f"Expected {expected_ranks}, "
        f"found {actual_ranks}"
    )

pass_msg(
    "Ranking sequence is contiguous from 1 to 8."
)


# =============================================================================
# PRIORITY VALIDATION
# =============================================================================

section("PRIORITY VALIDATION")

valid_priorities = {
    "higher_priority_candidate",
    "moderate_priority_candidate",
    "lower_priority_candidate",
}

priority_values = set(
    decision_support[
        "review_priority"
    ].dropna().astype(str)
)

invalid_priorities = (
    priority_values -
    valid_priorities
)

if invalid_priorities:
    fail(
        f"Invalid priority categories: "
        f"{sorted(invalid_priorities)}"
    )

pass_msg(
    "All review-priority categories are valid."
)


priority_counts = (
    decision_support[
        "review_priority"
    ]
    .value_counts()
    .to_dict()
)

higher_count = priority_counts.get(
    "higher_priority_candidate",
    0
)

moderate_count = priority_counts.get(
    "moderate_priority_candidate",
    0
)

lower_count = priority_counts.get(
    "lower_priority_candidate",
    0
)


print(
    f"Higher priority   : {higher_count}"
)

print(
    f"Moderate priority : {moderate_count}"
)

print(
    f"Lower priority    : {lower_count}"
)


if higher_count != 1:
    fail(
        "Expected 1 higher-priority candidate."
    )

if moderate_count != 2:
    fail(
        "Expected 2 moderate-priority candidates."
    )

if lower_count != 5:
    fail(
        "Expected 5 lower-priority candidates."
    )

pass_msg(
    "Priority distribution matches Phase 9 analysis."
)


# =============================================================================
# PRIORITY CANDIDATE CHECK
# =============================================================================

section("PRIORITY CANDIDATE CHECK")

priority_lookup = dict(
    zip(
        decision_support[
            "reactionmeddrapt"
        ],
        decision_support[
            "review_priority"
        ]
    )
)


expected_priority = {
    "Acute kidney injury":
        "higher_priority_candidate",

    "Drug ineffective":
        "moderate_priority_candidate",

    "Hypokalaemia":
        "moderate_priority_candidate",

    "Cholestasis":
        "lower_priority_candidate",

    "Hyponatraemia":
        "lower_priority_candidate",

    "Drug interaction":
        "lower_priority_candidate",

    "Hepatic cytolysis":
        "lower_priority_candidate",

    "Joint swelling":
        "lower_priority_candidate",
}


for reaction, expected in (
    expected_priority.items()
):

    actual = priority_lookup.get(
        reaction
    )

    if actual != expected:
        fail(
            f"{reaction}: expected "
            f"{expected}, found {actual}"
        )

    pass_msg(
        f"{reaction}: {expected}"
    )


# =============================================================================
# SERIOUSNESS LOGIC
# =============================================================================

section("SERIOUSNESS VALIDATION")

reported = pd.to_numeric(
    decision_support[
        "reported_cases"
    ],
    errors="coerce"
)

serious = pd.to_numeric(
    decision_support[
        "serious_cases"
    ],
    errors="coerce"
)

deaths = pd.to_numeric(
    decision_support[
        "death_cases"
    ],
    errors="coerce"
)

hospitalizations = pd.to_numeric(
    decision_support[
        "hospitalization_cases"
    ],
    errors="coerce"
)


if (
    reported.isna().any()
    or serious.isna().any()
    or deaths.isna().any()
    or hospitalizations.isna().any()
):
    fail(
        "Non-numeric seriousness counts detected."
    )


if (reported < 0).any():
    fail(
        "Negative reported-case count detected."
    )

if (serious < 0).any():
    fail(
        "Negative serious-case count detected."
    )

if (deaths < 0).any():
    fail(
        "Negative death count detected."
    )

if (hospitalizations < 0).any():
    fail(
        "Negative hospitalization count detected."
    )


if (serious > reported).any():
    fail(
        "Serious cases exceed reported cases."
    )

if (deaths > reported).any():
    fail(
        "Death cases exceed reported cases."
    )

if (hospitalizations > reported).any():
    fail(
        "Hospitalizations exceed reported cases."
    )

pass_msg(
    "Seriousness counts are logically valid."
)


# =============================================================================
# PERCENTAGE VALIDATION
# =============================================================================

section("PERCENTAGE VALIDATION")

for column in [
    "percentage_of_all_cases",
    "serious_percentage",
]:

    values = pd.to_numeric(
        decision_support[column],
        errors="coerce"
    )

    if values.isna().any():
        fail(
            f"Non-numeric values in {column}"
        )

    if (
        (values < 0)
        | (values > 100)
    ).any():
        fail(
            f"Invalid percentage values "
            f"in {column}"
        )

    pass_msg(column)


# =============================================================================
# RECOMMENDED ACTION VALIDATION
# =============================================================================

section("RECOMMENDED ACTION VALIDATION")

valid_actions = {
    "priority_detailed_review",
    "focused_review",
    "continued_monitoring",
}

actions = set(
    decision_support[
        "recommended_action"
    ].dropna().astype(str)
)

invalid_actions = (
    actions -
    valid_actions
)

if invalid_actions:
    fail(
        f"Invalid recommended action(s): "
        f"{sorted(invalid_actions)}"
    )

pass_msg(
    "Recommended actions are valid."
)


action_mapping = {
    "higher_priority_candidate":
        "priority_detailed_review",

    "moderate_priority_candidate":
        "focused_review",

    "lower_priority_candidate":
        "continued_monitoring",
}


for _, row in (
    decision_support.iterrows()
):

    expected_action = (
        action_mapping[
            row["review_priority"]
        ]
    )

    if (
        row["recommended_action"]
        != expected_action
    ):
        fail(
            f"Action mismatch for "
            f"{row['reactionmeddrapt']}"
        )

pass_msg(
    "Recommended actions match review priorities."
)


# =============================================================================
# ANALYTICAL SAFETY FLAGS
# =============================================================================

section("ANALYTICAL SAFETY VALIDATION")


false_columns = [
    "confirmed_signal",
    "frequency_is_incidence",
    "causality_established",
    "comparator_available",
    "ror_available",
    "prr_available",
    "disproportionality_established",
    "interaction_established",
]


for column in false_columns:

    values = (
        decision_support[column]
        .apply(to_bool)
    )

    if values.any():
        fail(
            f"Analytical safety violation: "
            f"{column} contains True."
        )

    pass_msg(
        f"{column} remains False."
    )


# =============================================================================
# SAFETY ASSESSMENT CHECK
# =============================================================================

section("SAFETY ASSESSMENT VALIDATION")

for column in [
    "confirmed_adverse_reaction",
    "confirmed_signal",
]:

    values = (
        safety_assessment[column]
        .apply(to_bool)
    )

    if values.any():
        fail(
            f"{column} incorrectly contains True."
        )

    pass_msg(
        f"{column} remains False."
    )


valid_causality_status = {
    "not_established"
}

valid_disprop_status = {
    "not_assessed"
}

valid_incidence_status = {
    "not_established"
}

valid_interaction_status = {
    "not_established"
}


if not set(
    safety_assessment[
        "causal_relationship"
    ].astype(str)
).issubset(
    valid_causality_status
):
    fail(
        "Invalid causal relationship status."
    )

pass_msg(
    "Causal relationship remains not established."
)


if not set(
    safety_assessment[
        "disproportionality_status"
    ].astype(str)
).issubset(
    valid_disprop_status
):
    fail(
        "Invalid disproportionality status."
    )

pass_msg(
    "Disproportionality remains not assessed."
)


if not set(
    safety_assessment[
        "incidence_status"
    ].astype(str)
).issubset(
    valid_incidence_status
):
    fail(
        "Invalid incidence status."
    )

pass_msg(
    "Incidence remains not established."
)


if not set(
    safety_assessment[
        "interaction_status"
    ].astype(str)
).issubset(
    valid_interaction_status
):
    fail(
        "Invalid interaction status."
    )

pass_msg(
    "Interaction remains not established."
)


# =============================================================================
# LIMITATION VALIDATION
# =============================================================================

section("LIMITATION VALIDATION")

if limitations[
    "limitation"
].isna().any():
    fail(
        "Missing limitation descriptions."
    )

if limitations[
    "impact"
].isna().any():
    fail(
        "Missing limitation impacts."
    )

if limitations[
    "restriction"
].isna().any():
    fail(
        "Missing analytical restrictions."
    )

pass_msg(
    "All limitation records are populated."
)


# =============================================================================
# SUMMARY VALIDATION
# =============================================================================

section("SUMMARY VALIDATION")

summary_row = summary.iloc[0]


integrated_cases = int(
    float(
        summary_row[
            "integrated_cases"
        ]
    )
)

bisoprolol_cases = int(
    float(
        summary_row[
            "bisoprolol_cases"
        ]
    )
)

candidate_reactions = int(
    float(
        summary_row[
            "candidate_reactions"
        ]
    )
)


print(
    f"Integrated cases    : "
    f"{integrated_cases:,}"
)

print(
    f"Bisoprolol cases    : "
    f"{bisoprolol_cases:,}"
)

print(
    f"Candidate reactions : "
    f"{candidate_reactions}"
)


if integrated_cases != 1024:
    fail(
        f"Expected 1,024 integrated cases, "
        f"found {integrated_cases:,}"
    )

pass_msg(
    "Integrated cases: 1,024"
)


if bisoprolol_cases != 1024:
    fail(
        f"Expected 1,024 Bisoprolol cases, "
        f"found {bisoprolol_cases:,}"
    )

pass_msg(
    "Bisoprolol cases: 1,024"
)


if candidate_reactions != 8:
    fail(
        f"Expected 8 candidate reactions, "
        f"found {candidate_reactions}"
    )

pass_msg(
    "Candidate reactions: 8"
)


# =============================================================================
# SUMMARY PRIORITY COUNTS
# =============================================================================

section("SUMMARY PRIORITY VALIDATION")


summary_higher = int(
    float(
        summary_row[
            "higher_priority_candidates"
        ]
    )
)

summary_moderate = int(
    float(
        summary_row[
            "moderate_priority_candidates"
        ]
    )
)

summary_lower = int(
    float(
        summary_row[
            "lower_priority_candidates"
        ]
    )
)


if summary_higher != higher_count:
    fail(
        "Higher-priority summary count mismatch."
    )

if summary_moderate != moderate_count:
    fail(
        "Moderate-priority summary count mismatch."
    )

if summary_lower != lower_count:
    fail(
        "Lower-priority summary count mismatch."
    )

pass_msg(
    "Summary priority counts match "
    "decision-support dataset."
)


# =============================================================================
# TOP CANDIDATE VALIDATION
# =============================================================================

section("TOP CANDIDATE VALIDATION")

top_candidate = str(
    summary_row[
        "top_candidate"
    ]
).strip()

top_cases = int(
    float(
        summary_row[
            "top_candidate_cases"
        ]
    )
)

top_priority = str(
    summary_row[
        "top_candidate_priority"
    ]
).strip()


if top_candidate != "Acute kidney injury":
    fail(
        f"Unexpected top candidate: "
        f"{top_candidate}"
    )

pass_msg(
    "Top candidate: Acute kidney injury"
)


if top_cases != 22:
    fail(
        f"Expected 22 top-candidate cases, "
        f"found {top_cases}"
    )

pass_msg(
    "Top candidate case count: 22"
)


if (
    top_priority
    != "higher_priority_candidate"
):
    fail(
        f"Unexpected top-candidate priority: "
        f"{top_priority}"
    )

pass_msg(
    "Top candidate priority: "
    "higher_priority_candidate"
)


# =============================================================================
# SUMMARY SAFETY FLAGS
# =============================================================================

section("SUMMARY ANALYTICAL SAFETY")

summary_false_flags = [
    "comparator_available",
    "ror_available",
    "prr_available",
    "frequency_is_incidence",
    "causality_established",
    "disproportionality_established",
    "co_medication_interaction_established",
    "confirmed_signal_established",
]


for column in summary_false_flags:

    value = to_bool(
        summary_row[column]
    )

    if value:
        fail(
            f"Summary analytical safety "
            f"violation: {column} = True"
        )

    pass_msg(
        f"{column} remains False."
    )


# =============================================================================
# DECISION-SCOPE VALIDATION
# =============================================================================

section("DECISION SCOPE VALIDATION")

expected_scope = (
    "pharmacovigilance_review_prioritization_only"
)

if not (
    decision_support[
        "decision_scope"
    ].astype(str)
    == expected_scope
).all():

    fail(
        "Unexpected decision-support scope."
    )

pass_msg(
    "Decision support is restricted to "
    "pharmacovigilance review prioritization."
)


if (
    str(
        summary_row[
            "decision_scope"
        ]
    ).strip()
    != "review_prioritization_only"
):
    fail(
        "Unexpected Phase 9 summary "
        "decision scope."
    )

pass_msg(
    "Phase 9 summary decision scope is valid."
)


# =============================================================================
# FINAL RESULT
# =============================================================================

section("FINAL RESULT")

print("PASS")

print()

print(
    "Phase 9 final pharmacovigilance "
    "decision-support analysis is structurally valid."
)

print()

print("Phase status:")

print(
    "Phase 1 - Drug normalization        : COMPLETE"
)

print(
    "Phase 2 - Reaction normalization    : COMPLETE"
)

print(
    "Phase 3 - Structure validation      : COMPLETE"
)

print(
    "Phase 4 - Case integration          : COMPLETE"
)

print(
    "Phase 5 - Pharmacovigilance screen  : COMPLETE"
)

print(
    "Phase 6 - Signal pattern analysis   : COMPLETE"
)

print(
    "Phase 7 - Evidence & reporting      : COMPLETE"
)

print(
    "Phase 8 - Structured reporting      : COMPLETE"
)

print(
    "Phase 9 - Decision support          : COMPLETE"
)

print()

print("Review-priority distribution:")

print(
    f"Higher priority   : {higher_count}"
)

print(
    f"Moderate priority : {moderate_count}"
)

print(
    f"Lower priority    : {lower_count}"
)

print()

print("IMPORTANT:")

print(
    "Priority categories are review-priority "
    "classifications only."
)

print(
    "They do not represent confirmed safety signals."
)

print(
    "No internal non-Bisoprolol comparator exists."
)

print(
    "ROR/PRR are not calculated."
)

print(
    "Frequency is not interpreted as incidence."
)

print(
    "Causality is not established."
)

print(
    "Disproportionality is not established."
)

print(
    "Co-medication patterns do not establish interactions."
)

print(
    "All findings remain descriptive/exploratory."
)

print()

print("=" * 100)