import os
import sys
import json
import pandas as pd
from datetime import datetime


# =============================================================================
# PHASE 10 - PREPARE CONTROLLED GENAI CONTEXT
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

OUTPUT_JSON = os.path.join(
    DATA_DIR,
    "phase10_genai_context.json"
)

OUTPUT_CANDIDATES_JSON = os.path.join(
    DATA_DIR,
    "phase10_candidate_context.json"
)

OUTPUT_RULES_JSON = os.path.join(
    DATA_DIR,
    "phase10_reporting_rules.json"
)


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

    fail(
        f"Unable to interpret boolean value: {value}"
    )


def safe_int(value):
    if pd.isna(value):
        return 0

    try:
        return int(float(value))
    except Exception:
        return 0


def safe_float(value):
    if pd.isna(value):
        return 0.0

    try:
        return float(value)
    except Exception:
        return 0.0


def safe_text(value):
    if pd.isna(value):
        return ""

    return str(value).strip()


def records_to_clean_dicts(df):
    records = []

    for _, row in df.iterrows():

        record = {}

        for column in df.columns:

            value = row[column]

            if pd.isna(value):
                record[column] = None

            elif isinstance(value, bool):
                record[column] = value

            elif hasattr(value, "item"):
                try:
                    record[column] = value.item()
                except Exception:
                    record[column] = value

            else:
                record[column] = value

        records.append(record)

    return records


# =============================================================================
# HEADER
# =============================================================================

header(
    "PHASE 10 - CONTROLLED GENAI CONTEXT PREPARATION"
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
            f"Required Phase 9 file missing: "
            f"{filename}"
        )

    pass_msg(filename)


# =============================================================================
# LOAD PHASE 9 DATA
# =============================================================================

section("LOADING PHASE 9 DATA")

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
    f"Signal assessment rows : "
    f"{len(signal_assessment):,}"
)

print(
    f"Candidate summaries    : "
    f"{len(candidate_summaries):,}"
)

print(
    f"Safety assessments     : "
    f"{len(safety_assessment):,}"
)

print(
    f"Limitations            : "
    f"{len(limitations):,}"
)

print(
    f"Decision support rows  : "
    f"{len(decision_support):,}"
)

print(
    f"Summary rows           : "
    f"{len(summary):,}"
)


# =============================================================================
# BASIC STRUCTURE VALIDATION
# =============================================================================

section("STRUCTURE VALIDATION")

if len(summary) != 1:
    fail(
        "Phase 9 summary must contain exactly "
        "one row."
    )

if len(candidate_summaries) != 8:
    fail(
        f"Expected 8 candidates, found "
        f"{len(candidate_summaries)}."
    )

if len(decision_support) != 8:
    fail(
        f"Expected 8 decision-support rows, found "
        f"{len(decision_support)}."
    )

if len(signal_assessment) != 8:
    fail(
        f"Expected 8 signal-assessment rows, found "
        f"{len(signal_assessment)}."
    )

pass_msg(
    "Expected Phase 9 dataset cardinality confirmed."
)


# =============================================================================
# CANDIDATE CONSISTENCY
# =============================================================================

section("CANDIDATE CONSISTENCY")

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

decision_candidates = set(
    decision_support[
        "reactionmeddrapt"
    ].astype(str).str.strip()
)

safety_candidates = set(
    safety_assessment[
        "reactionmeddrapt"
    ].astype(str).str.strip()
)


if signal_candidates != summary_candidates:
    fail(
        "Signal assessment and candidate-summary "
        "candidate sets do not match."
    )

if signal_candidates != decision_candidates:
    fail(
        "Signal assessment and decision-support "
        "candidate sets do not match."
    )

if signal_candidates != safety_candidates:
    fail(
        "Signal assessment and safety-assessment "
        "candidate sets do not match."
    )

pass_msg(
    "Candidate reaction sets are consistent."
)


# =============================================================================
# ANALYTICAL SAFETY GATE
# =============================================================================

section("ANALYTICAL SAFETY GATE")

summary_row = summary.iloc[0]


safety_flags = {
    "comparator_available":
        to_bool(
            summary_row[
                "comparator_available"
            ]
        ),

    "ror_available":
        to_bool(
            summary_row[
                "ror_available"
            ]
        ),

    "prr_available":
        to_bool(
            summary_row[
                "prr_available"
            ]
        ),

    "frequency_is_incidence":
        to_bool(
            summary_row[
                "frequency_is_incidence"
            ]
        ),

    "causality_established":
        to_bool(
            summary_row[
                "causality_established"
            ]
        ),

    "disproportionality_established":
        to_bool(
            summary_row[
                "disproportionality_established"
            ]
        ),

    "co_medication_interaction_established":
        to_bool(
            summary_row[
                "co_medication_interaction_established"
            ]
        ),

    "confirmed_signal_established":
        to_bool(
            summary_row[
                "confirmed_signal_established"
            ]
        ),
}


for name, value in safety_flags.items():

    print(
        f"{name:<42}: {value}"
    )

    if value:
        fail(
            f"Unsafe analytical state: "
            f"{name}=True"
        )


pass_msg(
    "All prohibited analytical claims remain False."
)


# =============================================================================
# MASTER REPORTING RULES
# =============================================================================

section("BUILDING GENAI REPORTING RULES")

reporting_rules = {
    "role": (
        "Generate human-readable pharmacovigilance "
        "summaries from validated structured data only."
    ),

    "allowed_tasks": [
        "Summarize validated candidate data.",
        "Explain review-priority categories.",
        "Describe reported-case frequencies.",
        "Describe seriousness information.",
        "Describe recommended follow-up actions.",
        "Describe analytical limitations.",
        "Generate an executive summary.",
        "Generate candidate-by-candidate report sections.",
    ],

    "prohibited_tasks": [
        "Do not invent case counts.",
        "Do not change percentages.",
        "Do not calculate ROR.",
        "Do not calculate PRR.",
        "Do not infer incidence.",
        "Do not claim causality.",
        "Do not claim disproportionality.",
        "Do not declare a confirmed safety signal.",
        "Do not declare a confirmed adverse reaction.",
        "Do not declare a confirmed drug-drug interaction.",
        "Do not create an artificial comparator cohort.",
        "Do not interpret review priority as causal importance.",
    ],

    "required_language": [
        (
            "Use 'reported cases' rather than "
            "'incidence' or 'risk'."
        ),
        (
            "Use 'review-priority candidate' rather than "
            "'confirmed signal'."
        ),
        (
            "State that causality is not established."
        ),
        (
            "State that disproportionality was not assessed "
            "because no internal non-Bisoprolol comparator "
            "was available."
        ),
        (
            "State that co-medication patterns do not "
            "establish drug-drug interactions."
        ),
    ],

    "numerical_integrity": {
        "numbers_must_match_context": True,
        "percentages_must_match_context": True,
        "ranking_must_match_context": True,
        "priority_must_match_context": True,
    },

    "interpretation_scope": (
        "Descriptive and exploratory "
        "pharmacovigilance review prioritization only."
    ),
}


print(
    "PASS - Controlled reporting rules prepared."
)


# =============================================================================
# BUILD CANDIDATE CONTEXT
# =============================================================================

section("BUILDING CANDIDATE CONTEXT")

candidate_context = []


candidate_summaries_sorted = (
    candidate_summaries
    .sort_values("rank")
    .reset_index(drop=True)
)


for _, candidate in (
    candidate_summaries_sorted.iterrows()
):

    reaction = safe_text(
        candidate[
            "reactionmeddrapt"
        ]
    )

    decision_match = (
        decision_support[
            decision_support[
                "reactionmeddrapt"
            ].astype(str).str.strip()
            == reaction
        ]
    )

    safety_match = (
        safety_assessment[
            safety_assessment[
                "reactionmeddrapt"
            ].astype(str).str.strip()
            == reaction
        ]
    )

    signal_match = (
        signal_assessment[
            signal_assessment[
                "reactionmeddrapt"
            ].astype(str).str.strip()
            == reaction
        ]
    )


    if len(decision_match) != 1:
        fail(
            f"Decision-support match problem for: "
            f"{reaction}"
        )

    if len(safety_match) != 1:
        fail(
            f"Safety-assessment match problem for: "
            f"{reaction}"
        )

    if len(signal_match) != 1:
        fail(
            f"Signal-assessment match problem for: "
            f"{reaction}"
        )


    decision = decision_match.iloc[0]
    safety = safety_match.iloc[0]
    signal = signal_match.iloc[0]


    context_item = {
        "rank":
            safe_int(
                candidate["rank"]
            ),

        "reaction":
            reaction,

        "reported_cases":
            safe_int(
                candidate[
                    "reported_cases"
                ]
            ),

        "percentage_of_all_cases":
            safe_float(
                candidate[
                    "percentage_of_all_cases"
                ]
            ),

        "serious_cases":
            safe_int(
                candidate[
                    "serious_cases"
                ]
            ),

        "serious_percentage":
            safe_float(
                candidate[
                    "serious_percentage"
                ]
            ),

        "death_cases":
            safe_int(
                candidate[
                    "death_cases"
                ]
            ),

        "hospitalization_cases":
            safe_int(
                candidate[
                    "hospitalization_cases"
                ]
            ),

        "evidence_level":
            safe_text(
                candidate[
                    "evidence_level"
                ]
            ),

        "review_priority":
            safe_text(
                candidate[
                    "review_priority"
                ]
            ),

        "recommended_action":
            safe_text(
                decision[
                    "recommended_action"
                ]
            ),

        "evidence_summary":
            safe_text(
                candidate[
                    "evidence_summary"
                ]
            ),

        "follow_up_recommendation":
            safe_text(
                candidate[
                    "follow_up_recommendation"
                ]
            ),

        "interpretation_scope":
            safe_text(
                candidate[
                    "interpretation_scope"
                ]
            ),

        "requires_case_review":
            to_bool(
                safety[
                    "requires_case_review"
                ]
            ),

        "confirmed_signal":
            to_bool(
                signal[
                    "confirmed_signal"
                ]
            ),

        "confirmed_adverse_reaction":
            to_bool(
                safety[
                    "confirmed_adverse_reaction"
                ]
            ),

        "causality_established":
            to_bool(
                signal[
                    "causality_established"
                ]
            ),

        "disproportionality_established":
            to_bool(
                signal[
                    "disproportionality_established"
                ]
            ),

        "incidence_established":
            to_bool(
                signal[
                    "incidence_established"
                ]
            ),

        "interaction_established":
            to_bool(
                signal[
                    "interaction_established"
                ]
            ),
    }


    prohibited_flags = [
        "confirmed_signal",
        "confirmed_adverse_reaction",
        "causality_established",
        "disproportionality_established",
        "incidence_established",
        "interaction_established",
    ]


    for flag in prohibited_flags:

        if context_item[flag]:
            fail(
                f"Unsafe candidate state for "
                f"{reaction}: {flag}=True"
            )


    candidate_context.append(
        context_item
    )


print(
    f"PASS - Candidate contexts created: "
    f"{len(candidate_context)}"
)


# =============================================================================
# BUILD LIMITATION CONTEXT
# =============================================================================

section("BUILDING LIMITATION CONTEXT")

limitation_context = []


for _, row in limitations.sort_values(
    "limitation_id"
).iterrows():

    limitation_context.append({
        "limitation_id":
            safe_int(
                row[
                    "limitation_id"
                ]
            ),

        "limitation":
            safe_text(
                row[
                    "limitation"
                ]
            ),

        "impact":
            safe_text(
                row[
                    "impact"
                ]
            ),

        "restriction":
            safe_text(
                row[
                    "restriction"
                ]
            ),
    })


print(
    f"PASS - Limitations added: "
    f"{len(limitation_context)}"
)


# =============================================================================
# BUILD DATASET SUMMARY
# =============================================================================

section("BUILDING DATASET SUMMARY CONTEXT")

dataset_summary = {
    "integrated_cases":
        safe_int(
            summary_row[
                "integrated_cases"
            ]
        ),

    "bisoprolol_cases":
        safe_int(
            summary_row[
                "bisoprolol_cases"
            ]
        ),

    "candidate_reactions":
        safe_int(
            summary_row[
                "candidate_reactions"
            ]
        ),

    "higher_priority_candidates":
        safe_int(
            summary_row[
                "higher_priority_candidates"
            ]
        ),

    "moderate_priority_candidates":
        safe_int(
            summary_row[
                "moderate_priority_candidates"
            ]
        ),

    "lower_priority_candidates":
        safe_int(
            summary_row[
                "lower_priority_candidates"
            ]
        ),

    "top_candidate":
        safe_text(
            summary_row[
                "top_candidate"
            ]
        ),

    "top_candidate_cases":
        safe_int(
            summary_row[
                "top_candidate_cases"
            ]
        ),

    "top_candidate_priority":
        safe_text(
            summary_row[
                "top_candidate_priority"
            ]
        ),

    "analysis_type":
        safe_text(
            summary_row[
                "analysis_type"
            ]
        ),

    "decision_scope":
        safe_text(
            summary_row[
                "decision_scope"
            ]
        ),

    "major_limitation":
        safe_text(
            summary_row[
                "major_limitation"
            ]
        ),

    "interpretation":
        safe_text(
            summary_row[
                "interpretation"
            ]
        ),
}


print(
    f"Integrated cases      : "
    f"{dataset_summary['integrated_cases']:,}"
)

print(
    f"Bisoprolol cases      : "
    f"{dataset_summary['bisoprolol_cases']:,}"
)

print(
    f"Candidate reactions   : "
    f"{dataset_summary['candidate_reactions']}"
)

print(
    f"Higher priority       : "
    f"{dataset_summary['higher_priority_candidates']}"
)

print(
    f"Moderate priority     : "
    f"{dataset_summary['moderate_priority_candidates']}"
)

print(
    f"Lower priority        : "
    f"{dataset_summary['lower_priority_candidates']}"
)

print(
    f"Top candidate         : "
    f"{dataset_summary['top_candidate']}"
)


# =============================================================================
# CREATE MASTER GENAI CONTEXT
# =============================================================================

section("CREATING MASTER GENAI CONTEXT")

master_context = {
    "context_version": "phase10_v1",

    "project": {
        "name": "GenAR-PADER-AI",
        "analysis_domain": "pharmacovigilance",
        "drug_scope": "Bisoprolol-containing safety reports",
        "report_type": (
            "descriptive exploratory "
            "pharmacovigilance report"
        ),
    },

    "dataset_summary":
        dataset_summary,

    "analytical_safety": {
        "comparator_available": False,
        "ror_available": False,
        "prr_available": False,
        "frequency_is_incidence": False,
        "causality_established": False,
        "disproportionality_established": False,
        "confirmed_signal_established": False,
        "drug_interaction_established": False,
    },

    "reporting_rules":
        reporting_rules,

    "candidates":
        candidate_context,

    "analytical_limitations":
        limitation_context,

    "required_report_sections": [
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
    ],

    "generation_instruction": (
        "Generate a human-readable pharmacovigilance "
        "report using only facts contained in this "
        "context. Do not introduce external numerical "
        "claims or unsupported causal interpretations."
    ),
}


# =============================================================================
# WRITE MASTER CONTEXT
# =============================================================================

section("WRITING GENAI CONTEXT FILES")

with open(
    OUTPUT_JSON,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        master_context,
        file,
        indent=2,
        ensure_ascii=False
    )


pass_msg(
    "phase10_genai_context.json created."
)


# =============================================================================
# WRITE CANDIDATE CONTEXT
# =============================================================================

with open(
    OUTPUT_CANDIDATES_JSON,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        {
            "candidate_count":
                len(candidate_context),

            "candidates":
                candidate_context,
        },
        file,
        indent=2,
        ensure_ascii=False
    )


pass_msg(
    "phase10_candidate_context.json created."
)


# =============================================================================
# WRITE REPORTING RULES
# =============================================================================

with open(
    OUTPUT_RULES_JSON,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        reporting_rules,
        file,
        indent=2,
        ensure_ascii=False
    )


pass_msg(
    "phase10_reporting_rules.json created."
)


# =============================================================================
# OUTPUT VALIDATION
# =============================================================================

section("OUTPUT VALIDATION")


required_output_files = [
    OUTPUT_JSON,
    OUTPUT_CANDIDATES_JSON,
    OUTPUT_RULES_JSON,
]


for output_file in required_output_files:

    if not os.path.exists(output_file):
        fail(
            f"Output file missing: "
            f"{output_file}"
        )

    if os.path.getsize(output_file) == 0:
        fail(
            f"Output file is empty: "
            f"{output_file}"
        )

    pass_msg(
        os.path.basename(
            output_file
        )
    )


# =============================================================================
# READ-BACK VALIDATION
# =============================================================================

section("JSON READ-BACK VALIDATION")


with open(
    OUTPUT_JSON,
    "r",
    encoding="utf-8"
) as file:

    loaded_context = json.load(file)


if (
    loaded_context[
        "dataset_summary"
    ][
        "integrated_cases"
    ]
    != dataset_summary[
        "integrated_cases"
    ]
):
    fail(
        "Integrated case count changed "
        "during JSON serialization."
    )


if (
    len(
        loaded_context[
            "candidates"
        ]
    )
    != 8
):
    fail(
        "Candidate count changed during "
        "JSON serialization."
    )


if (
    loaded_context[
        "analytical_safety"
    ][
        "causality_established"
    ]
):
    fail(
        "Causality safety flag changed "
        "during serialization."
    )


if (
    loaded_context[
        "analytical_safety"
    ][
        "confirmed_signal_established"
    ]
):
    fail(
        "Confirmed-signal safety flag "
        "changed during serialization."
    )


pass_msg(
    "Master JSON context validated."
)


# =============================================================================
# CONTEXT PREVIEW
# =============================================================================

section("GENAI CONTEXT PREVIEW")


print(
    f"Context version       : "
    f"{master_context['context_version']}"
)

print(
    f"Project               : "
    f"{master_context['project']['name']}"
)

print(
    f"Integrated cases      : "
    f"{dataset_summary['integrated_cases']:,}"
)

print(
    f"Bisoprolol cases      : "
    f"{dataset_summary['bisoprolol_cases']:,}"
)

print(
    f"Candidate reactions   : "
    f"{len(candidate_context)}"
)

print(
    f"Top candidate         : "
    f"{dataset_summary['top_candidate']}"
)

print(
    f"Top candidate cases   : "
    f"{dataset_summary['top_candidate_cases']}"
)


print()
print("Candidate priorities:")

for item in candidate_context:

    print(
        f"  {item['rank']:02d}. "
        f"{item['reaction']:<35} "
        f"{item['review_priority']}"
    )


# =============================================================================
# SAFETY SUMMARY
# =============================================================================

section("GENAI SAFETY SUMMARY")

print(
    "Comparator available            : False"
)

print(
    "ROR available                   : False"
)

print(
    "PRR available                   : False"
)

print(
    "Frequency interpreted as incidence : False"
)

print(
    "Causality established           : False"
)

print(
    "Disproportionality established  : False"
)

print(
    "Confirmed signal established    : False"
)

print(
    "Drug interaction established    : False"
)


# =============================================================================
# COMPLETE
# =============================================================================

header(
    "PHASE 10 GENAI CONTEXT PREPARATION COMPLETE"
)

print(
    "Generated files:"
)

print(
    " - data\\phase10_genai_context.json"
)

print(
    " - data\\phase10_candidate_context.json"
)

print(
    " - data\\phase10_reporting_rules.json"
)

print()

print(
    "The validated Phase 9 results have now been "
    "converted into a controlled machine-readable "
    "context for the GenAI reporting layer."
)

print()

print(
    "Next step:"
)

print(
    "generate_phase10_report.py"
)
