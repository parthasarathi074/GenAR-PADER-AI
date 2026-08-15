import os
import pandas as pd


# =============================================================================
# PHASE 9 - FINAL PHARMACOVIGILANCE DECISION SUPPORT ANALYSIS
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

REPORTING_FILE = os.path.join(DATA_DIR, "phase8_structured_reporting.csv")
CARDS_FILE = os.path.join(DATA_DIR, "phase8_candidate_report_cards.csv")
SUMMARY_FILE = os.path.join(DATA_DIR, "phase8_analysis_summary.csv")

OUTPUT_ASSESSMENT = os.path.join(DATA_DIR, "phase9_signal_assessment.csv")
OUTPUT_SUMMARIES = os.path.join(DATA_DIR, "phase9_candidate_summaries.csv")
OUTPUT_SAFETY = os.path.join(DATA_DIR, "phase9_safety_assessment.csv")
OUTPUT_LIMITATIONS = os.path.join(DATA_DIR, "phase9_limitation_assessment.csv")
OUTPUT_DECISION = os.path.join(DATA_DIR, "phase9_decision_support.csv")
OUTPUT_SUMMARY = os.path.join(DATA_DIR, "phase9_analysis_summary.csv")


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


def to_bool(value):
    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()

    if text in {"true", "1", "yes"}:
        return True

    if text in {"false", "0", "no"}:
        return False

    raise ValueError(f"Cannot convert value to boolean: {value}")


def safe_int(value):
    if pd.isna(value):
        return 0
    return int(float(value))


def safe_float(value):
    if pd.isna(value):
        return 0.0
    return float(value)


# =============================================================================
# START
# =============================================================================

header("PHASE 9 - FINAL PHARMACOVIGILANCE DECISION SUPPORT ANALYSIS")


# =============================================================================
# FILE CHECK
# =============================================================================

section("FILE CHECK")

required_files = [
    REPORTING_FILE,
    CARDS_FILE,
    SUMMARY_FILE,
]

for path in required_files:
    if not os.path.exists(path):
        fail(f"Required file missing: {os.path.basename(path)}")

    print(f"PASS - {os.path.basename(path)}")


# =============================================================================
# LOAD DATA
# =============================================================================

section("LOADING PHASE 8 OUTPUTS")

reporting = pd.read_csv(REPORTING_FILE)
cards = pd.read_csv(CARDS_FILE)
summary = pd.read_csv(SUMMARY_FILE)

print(f"Structured reporting rows : {len(reporting):,}")
print(f"Candidate cards           : {len(cards):,}")
print(f"Summary rows              : {len(summary):,}")

if len(summary) != 1:
    fail("Phase 8 summary must contain exactly one row.")

summary_row = summary.iloc[0]


# =============================================================================
# ANALYTICAL SAFETY CHECK
# =============================================================================

section("ANALYTICAL SAFETY CHECK")

comparator_available = to_bool(summary_row["comparator_available"])
ror_available = to_bool(summary_row["ror_available"])
prr_available = to_bool(summary_row["prr_available"])
frequency_is_incidence = to_bool(summary_row["frequency_is_incidence"])
causality_established = to_bool(summary_row["causality_established"])
disproportionality_established = to_bool(
    summary_row["disproportionality_established"]
)
interaction_established = to_bool(
    summary_row["co_medication_interaction_established"]
)

print(f"Comparator available              : {comparator_available}")
print(f"ROR available                     : {ror_available}")
print(f"PRR available                     : {prr_available}")
print(f"Frequency interpreted as incidence: {frequency_is_incidence}")
print(f"Causality established             : {causality_established}")
print(
    f"Disproportionality established    : "
    f"{disproportionality_established}"
)
print(f"Interaction established           : {interaction_established}")

if comparator_available:
    fail("Unexpected comparator detected.")

if ror_available or prr_available:
    fail("ROR/PRR must remain unavailable.")

if frequency_is_incidence:
    fail("Frequency must not be interpreted as incidence.")

if causality_established:
    fail("Causality must remain unestablished.")

if disproportionality_established:
    fail("Disproportionality must remain unestablished.")

if interaction_established:
    fail("Interaction must remain unestablished.")

print("PASS - Analytical restrictions preserved.")


# =============================================================================
# SORT CANDIDATES
# =============================================================================

cards = cards.sort_values("rank").reset_index(drop=True)


# =============================================================================
# REVIEW PRIORITY FUNCTION
# =============================================================================

def determine_review_priority(row):
    """
    Review priority is a descriptive triage category only.

    It is NOT:
    - a causal classification
    - a confirmed signal
    - a disproportionality result
    - an incidence classification
    """

    cases = safe_int(row["reported_cases"])
    deaths = safe_int(row["death_cases"])
    hospitalizations = safe_int(row["hospitalization_cases"])
    evidence_level = str(row["evidence_level"]).strip()

    if (
        evidence_level == "higher_frequency_candidate"
        or cases >= 20
        or deaths > 0
    ):
        return "higher_priority_candidate"

    if (
        evidence_level == "moderate_frequency_candidate"
        or cases >= 10
        or hospitalizations >= 5
    ):
        return "moderate_priority_candidate"

    return "lower_priority_candidate"


def determine_follow_up(priority):
    if priority == "higher_priority_candidate":
        return (
            "Prioritize for detailed case review, temporal assessment, "
            "clinical context review, confounder assessment, and external "
            "evidence evaluation."
        )

    if priority == "moderate_priority_candidate":
        return (
            "Perform focused case review and evaluate clinical context, "
            "co-medications, underlying disease, temporal information, "
            "and external evidence."
        )

    return (
        "Continue descriptive monitoring and review if additional cases "
        "or supporting evidence become available."
    )


def build_interpretation(row, priority):
    reaction = str(row["reaction"])
    cases = safe_int(row["reported_cases"])
    percentage = safe_float(row["percentage_of_all_cases"])
    serious = safe_int(row["serious_cases"])
    deaths = safe_int(row["death_cases"])
    hospitalizations = safe_int(row["hospitalization_cases"])

    return (
        f"{reaction} was reported in {cases} Bisoprolol-containing cases "
        f"({percentage:.2f}% of the analyzed cohort). "
        f"{serious} cases were classified as serious, including "
        f"{deaths} death-associated case(s) and "
        f"{hospitalizations} hospitalization-associated case(s). "
        f"The candidate is assigned {priority} for review purposes only. "
        f"This classification does not establish causality, incidence, "
        f"disproportionality, or a confirmed safety signal."
    )


# =============================================================================
# BUILD SIGNAL ASSESSMENT
# =============================================================================

section("BUILDING CANDIDATE SIGNAL ASSESSMENT")

assessment_rows = []

for _, row in cards.iterrows():

    priority = determine_review_priority(row)

    assessment_rows.append({
        "rank": safe_int(row["rank"]),
        "reactionmeddrapt": str(row["reaction"]),
        "reported_cases": safe_int(row["reported_cases"]),
        "percentage_of_all_cases":
            safe_float(row["percentage_of_all_cases"]),
        "serious_cases": safe_int(row["serious_cases"]),
        "serious_percentage":
            safe_float(row["serious_percentage"]),
        "death_cases": safe_int(row["death_cases"]),
        "hospitalization_cases":
            safe_int(row["hospitalization_cases"]),
        "evidence_level": str(row["evidence_level"]),
        "review_priority": priority,
        "confirmed_signal": False,
        "causality_established": False,
        "disproportionality_established": False,
        "incidence_established": False,
        "interaction_established": False,
        "analysis_type": "descriptive_exploratory",
    })

signal_assessment = pd.DataFrame(assessment_rows)

signal_assessment.to_csv(
    OUTPUT_ASSESSMENT,
    index=False
)

print("PASS - Signal assessment created:")
print(OUTPUT_ASSESSMENT)


# =============================================================================
# BUILD CANDIDATE SUMMARIES
# =============================================================================

section("BUILDING CANDIDATE EVIDENCE SUMMARIES")

summary_rows = []

for _, row in cards.iterrows():

    priority = determine_review_priority(row)

    summary_rows.append({
        "rank": safe_int(row["rank"]),
        "reactionmeddrapt": str(row["reaction"]),
        "reported_cases": safe_int(row["reported_cases"]),
        "percentage_of_all_cases":
            safe_float(row["percentage_of_all_cases"]),
        "serious_cases": safe_int(row["serious_cases"]),
        "serious_percentage":
            safe_float(row["serious_percentage"]),
        "death_cases": safe_int(row["death_cases"]),
        "hospitalization_cases":
            safe_int(row["hospitalization_cases"]),
        "evidence_level": str(row["evidence_level"]),
        "review_priority": priority,
        "evidence_summary":
            build_interpretation(row, priority),
        "follow_up_recommendation":
            determine_follow_up(priority),
        "interpretation_scope":
            "reported_case_pattern_only",
    })

candidate_summaries = pd.DataFrame(summary_rows)

candidate_summaries.to_csv(
    OUTPUT_SUMMARIES,
    index=False
)

print("PASS - Candidate summaries created:")
print(OUTPUT_SUMMARIES)


# =============================================================================
# SAFETY ASSESSMENT
# =============================================================================

section("BUILDING SAFETY ASSESSMENT")

safety_rows = []

for _, row in cards.iterrows():

    priority = determine_review_priority(row)

    safety_rows.append({
        "reactionmeddrapt": str(row["reaction"]),
        "review_priority": priority,
        "reported_cases": safe_int(row["reported_cases"]),
        "serious_cases": safe_int(row["serious_cases"]),
        "death_cases": safe_int(row["death_cases"]),
        "hospitalization_cases":
            safe_int(row["hospitalization_cases"]),
        "requires_case_review":
            priority in {
                "higher_priority_candidate",
                "moderate_priority_candidate"
            },
        "confirmed_adverse_reaction": False,
        "confirmed_signal": False,
        "causal_relationship": "not_established",
        "disproportionality_status": "not_assessed",
        "incidence_status": "not_established",
        "interaction_status": "not_established",
    })

safety_assessment = pd.DataFrame(safety_rows)

safety_assessment.to_csv(
    OUTPUT_SAFETY,
    index=False
)

print("PASS - Safety assessment created:")
print(OUTPUT_SAFETY)


# =============================================================================
# LIMITATION ASSESSMENT
# =============================================================================

section("BUILDING ANALYTICAL LIMITATION ASSESSMENT")

limitations = [
    {
        "limitation_id": 1,
        "limitation":
            "No internal non-Bisoprolol comparator cohort is available.",
        "impact":
            "ROR and PRR cannot be calculated from this dataset.",
        "restriction":
            "No disproportionality conclusion is permitted."
    },
    {
        "limitation_id": 2,
        "limitation":
            "The dataset consists of reported safety cases.",
        "impact":
            "Reporting frequency does not provide an incidence denominator.",
        "restriction":
            "Reported percentages must not be interpreted as incidence."
    },
    {
        "limitation_id": 3,
        "limitation":
            "Observed candidate reactions are descriptive case patterns.",
        "impact":
            "Temporal, clinical, and confounding information may be incomplete.",
        "restriction":
            "Causality must not be inferred from frequency alone."
    },
    {
        "limitation_id": 4,
        "limitation":
            "Multiple concomitant medications occur in many cases.",
        "impact":
            "Alternative drug-related explanations may exist.",
        "restriction":
            "Co-medication presence does not establish interaction."
    },
    {
        "limitation_id": 5,
        "limitation":
            "Spontaneous safety-report data may contain reporting biases.",
        "impact":
            "Observed reporting patterns may not reflect underlying risk.",
        "restriction":
            "Candidate ranking is review prioritization only."
    },
]

limitation_assessment = pd.DataFrame(limitations)

limitation_assessment.to_csv(
    OUTPUT_LIMITATIONS,
    index=False
)

print("PASS - Limitation assessment created:")
print(OUTPUT_LIMITATIONS)


# =============================================================================
# DECISION SUPPORT DATASET
# =============================================================================

section("BUILDING DECISION SUPPORT DATASET")

decision_rows = []

for _, row in cards.iterrows():

    priority = determine_review_priority(row)

    if priority == "higher_priority_candidate":
        action = "priority_detailed_review"
    elif priority == "moderate_priority_candidate":
        action = "focused_review"
    else:
        action = "continued_monitoring"

    decision_rows.append({
        "rank": safe_int(row["rank"]),
        "reactionmeddrapt": str(row["reaction"]),
        "reported_cases": safe_int(row["reported_cases"]),
        "percentage_of_all_cases":
            safe_float(row["percentage_of_all_cases"]),
        "serious_cases": safe_int(row["serious_cases"]),
        "serious_percentage":
            safe_float(row["serious_percentage"]),
        "death_cases": safe_int(row["death_cases"]),
        "hospitalization_cases":
            safe_int(row["hospitalization_cases"]),
        "evidence_level": str(row["evidence_level"]),
        "review_priority": priority,
        "recommended_action": action,
        "confirmed_signal": False,
        "frequency_is_incidence": False,
        "causality_established": False,
        "comparator_available": False,
        "ror_available": False,
        "prr_available": False,
        "disproportionality_established": False,
        "interaction_established": False,
        "decision_scope":
            "pharmacovigilance_review_prioritization_only",
    })

decision_support = pd.DataFrame(decision_rows)

decision_support.to_csv(
    OUTPUT_DECISION,
    index=False
)

print("PASS - Decision support dataset created:")
print(OUTPUT_DECISION)


# =============================================================================
# PHASE 9 SUMMARY
# =============================================================================

section("BUILDING PHASE 9 ANALYSIS SUMMARY")

priority_counts = (
    decision_support["review_priority"]
    .value_counts()
    .to_dict()
)

top = decision_support.sort_values("rank").iloc[0]

phase9_summary = pd.DataFrame([{
    "integrated_cases":
        safe_int(summary_row["integrated_cases"]),
    "bisoprolol_cases":
        safe_int(summary_row["bisoprolol_cases"]),
    "candidate_reactions":
        len(decision_support),
    "higher_priority_candidates":
        priority_counts.get(
            "higher_priority_candidate", 0
        ),
    "moderate_priority_candidates":
        priority_counts.get(
            "moderate_priority_candidate", 0
        ),
    "lower_priority_candidates":
        priority_counts.get(
            "lower_priority_candidate", 0
        ),
    "top_candidate":
        str(top["reactionmeddrapt"]),
    "top_candidate_cases":
        safe_int(top["reported_cases"]),
    "top_candidate_priority":
        str(top["review_priority"]),
    "comparator_available": False,
    "ror_available": False,
    "prr_available": False,
    "frequency_is_incidence": False,
    "causality_established": False,
    "disproportionality_established": False,
    "co_medication_interaction_established": False,
    "confirmed_signal_established": False,
    "analysis_type":
        "descriptive_exploratory_decision_support",
    "decision_scope":
        "review_prioritization_only",
    "major_limitation":
        "No internal non-Bisoprolol comparator cohort.",
    "interpretation":
        (
            "Candidate priorities identify records for further "
            "pharmacovigilance review and do not establish safety signals, "
            "causality, incidence, disproportionality, or interactions."
        )
}])

phase9_summary.to_csv(
    OUTPUT_SUMMARY,
    index=False
)

print("PASS - Phase 9 summary created:")
print(OUTPUT_SUMMARY)


# =============================================================================
# PRIORITY RESULTS
# =============================================================================

section("PHASE 9 CANDIDATE PRIORITIZATION")

for _, row in decision_support.sort_values("rank").iterrows():

    print(
        f"{safe_int(row['rank']):02d}. "
        f"{row['reactionmeddrapt']:<35} "
        f"cases={safe_int(row['reported_cases']):>3} "
        f"serious={safe_int(row['serious_cases']):>3} "
        f"death={safe_int(row['death_cases']):>2} "
        f"hosp={safe_int(row['hospitalization_cases']):>3} "
        f"priority={row['review_priority']}"
    )


# =============================================================================
# PRIORITY DISTRIBUTION
# =============================================================================

section("REVIEW PRIORITY DISTRIBUTION")

for priority in [
    "higher_priority_candidate",
    "moderate_priority_candidate",
    "lower_priority_candidate",
]:

    count = priority_counts.get(priority, 0)

    print(
        f"{priority:<35}: {count}"
    )


# =============================================================================
# FINAL ANALYTICAL SAFETY
# =============================================================================

section("FINAL ANALYTICAL SAFETY")

print("Comparator cohort available          : NO")
print("ROR calculated                        : NO")
print("PRR calculated                        : NO")
print("Frequency interpreted as incidence   : NO")
print("Causality established                : NO")
print("Disproportionality established       : NO")
print("Confirmed safety signal established  : NO")
print("Drug-drug interaction established    : NO")

print()
print(
    "Priority classifications represent review priority only."
)

print(
    "They do not represent confirmed pharmacovigilance signals."
)


# =============================================================================
# COMPLETE
# =============================================================================

header("PHASE 9 ANALYSIS COMPLETE")

print("Generated files:")
print(" - phase9_signal_assessment.csv")
print(" - phase9_candidate_summaries.csv")
print(" - phase9_safety_assessment.csv")
print(" - phase9_limitation_assessment.csv")
print(" - phase9_decision_support.csv")
print(" - phase9_analysis_summary.csv")

print()
print(
    "Proceed to Phase 9 validation before starting the next phase."
)