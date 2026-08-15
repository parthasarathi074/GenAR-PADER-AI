import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_FILES = {
    "evidence": "phase7_candidate_evidence.csv",
    "ranking": "phase7_candidate_ranking.csv",
    "seriousness": "phase7_candidate_seriousness.csv",
    "demographics": "phase7_candidate_demographics.csv",
    "countries": "phase7_candidate_countries.csv",
    "products": "phase7_candidate_products.csv",
    "reporting": "phase7_reporting_matrix.csv",
    "summary": "phase7_analysis_summary.csv",
}


def header(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("-" * 100)


def path(filename):
    return os.path.join(DATA_DIR, filename)


header("PHASE 8 - STRUCTURED PHARMACOVIGILANCE REPORTING ANALYSIS")


section("FILE CHECK")

for name, filename in INPUT_FILES.items():

    if os.path.exists(path(filename)):
        print(f"PASS - {filename}")
    else:
        raise FileNotFoundError(f"Required file missing: {path(filename)}")


section("LOADING PHASE 7 DATASETS")

evidence = pd.read_csv(path(INPUT_FILES["evidence"]))
ranking = pd.read_csv(path(INPUT_FILES["ranking"]))
seriousness = pd.read_csv(path(INPUT_FILES["seriousness"]))
demographics = pd.read_csv(path(INPUT_FILES["demographics"]))
countries = pd.read_csv(path(INPUT_FILES["countries"]))
products = pd.read_csv(path(INPUT_FILES["products"]))
reporting = pd.read_csv(path(INPUT_FILES["reporting"]))
summary = pd.read_csv(path(INPUT_FILES["summary"]))

print(f"Evidence rows      : {len(evidence)}")
print(f"Ranking rows       : {len(ranking)}")
print(f"Seriousness rows   : {len(seriousness)}")
print(f"Demographic rows   : {len(demographics)}")
print(f"Country rows       : {len(countries)}")
print(f"Product rows       : {len(products)}")
print(f"Reporting rows     : {len(reporting)}")
print(f"Summary rows       : {len(summary)}")


section("ANALYTICAL SAFETY CHECK")

summary_row = summary.iloc[0]

comparator = bool(summary_row["comparator_available"])
ror_available = bool(summary_row["ror_available"])
prr_available = bool(summary_row["prr_available"])
causality = bool(summary_row["causality_established"])
disproportionality = bool(
    summary_row["disproportionality_established"]
)
frequency_incidence = bool(
    summary_row["frequency_is_incidence"]
)
interaction = bool(
    summary_row["co_medication_interaction_established"]
)

print(f"Comparator available              : {comparator}")
print(f"ROR available                     : {ror_available}")
print(f"PRR available                     : {prr_available}")
print(f"Frequency interpreted as incidence: {frequency_incidence}")
print(f"Causality established             : {causality}")
print(f"Disproportionality established    : {disproportionality}")
print(f"Interaction established           : {interaction}")


if comparator:
    raise ValueError(
        "Unexpected comparator availability. "
        "This Phase 8 workflow is designed for the current "
        "single-exposure dataset."
    )

if ror_available or prr_available:
    raise ValueError(
        "ROR/PRR cannot be accepted without a validated comparator."
    )

if causality:
    raise ValueError(
        "Causality must remain unestablished."
    )

if disproportionality:
    raise ValueError(
        "Disproportionality must remain unestablished."
    )

if frequency_incidence:
    raise ValueError(
        "Frequency must not be interpreted as incidence."
    )

if interaction:
    raise ValueError(
        "Co-medication patterns must not establish interaction."
    )

print("PASS - Analytical restrictions are preserved.")


section("BUILDING STRUCTURED REPORTING DATASET")

report = reporting.copy()

report["reporting_statement"] = (
    "Reported case pattern; frequency is descriptive and "
    "does not represent incidence."
)

report["clinical_interpretation"] = (
    "Candidate reaction identified through exploratory "
    "case-frequency screening."
)

report["causality_statement"] = (
    "Causality not established."
)

report["disproportionality_statement"] = (
    "Disproportionality not assessed because no internal "
    "non-Bisoprolol comparator cohort is available."
)

report["interaction_statement"] = (
    "Co-medication patterns are descriptive and do not "
    "establish drug-drug interaction."
)

report["comparator_statement"] = (
    "No internal non-Bisoprolol comparator cohort available."
)

report["reporting_scope"] = (
    "Descriptive pharmacovigilance evidence"
)

report["evidence_source"] = (
    "Integrated ICSR case-level dataset"
)

report["exposure_scope"] = (
    "Bisoprolol-containing safety reports"
)

report["analysis_restriction"] = (
    "Exploratory only; no causal, incidence, or "
    "disproportionality interpretation."
)

report.to_csv(
    path("phase8_structured_reporting.csv"),
    index=False
)

print(
    "PASS - Structured reporting dataset created:\n"
    + path("phase8_structured_reporting.csv")
)


section("BUILDING CANDIDATE REPORT CARDS")

cards = []

for _, row in ranking.sort_values("rank").iterrows():

    reaction = row["reactionmeddrapt"]

    evidence_row = evidence[
        evidence["reactionmeddrapt"] == reaction
    ]

    serious_row = seriousness[
        seriousness["reactionmeddrapt"] == reaction
    ]

    if len(evidence_row) == 0:
        continue

    e = evidence_row.iloc[0]

    if len(serious_row) > 0:
        s = serious_row.iloc[0]
    else:
        s = {}

    card = {
        "rank": int(row["rank"]),
        "reaction": reaction,
        "reported_cases": int(row["case_count"]),
        "percentage_of_all_cases": float(
            row["percentage_of_all_cases"]
        ),
        "serious_cases": int(
            row["serious_case_count"]
        ),
        "serious_percentage": float(
            row["serious_percentage"]
        ),
        "death_cases": int(
            e["death_case_count"]
        ),
        "hospitalization_cases": int(
            e["hospitalization_case_count"]
        ),
        "evidence_level": row["evidence_level"],
        "frequency_interpretation":
            "Descriptive reported-case frequency only",
        "causality":
            "Not established",
        "disproportionality":
            "Not assessed",
        "comparator":
            "Unavailable",
        "interaction":
            "Not established",
    }

    cards.append(card)

cards_df = pd.DataFrame(cards)

cards_df.to_csv(
    path("phase8_candidate_report_cards.csv"),
    index=False
)

print(
    "PASS - Candidate report cards created:\n"
    + path("phase8_candidate_report_cards.csv")
)


section("TOP CANDIDATE REPORT")

if len(cards_df) > 0:

    top = cards_df.sort_values("rank").iloc[0]

    print(f"Rank                : {int(top['rank'])}")
    print(f"Reaction            : {top['reaction']}")
    print(f"Reported cases      : {int(top['reported_cases'])}")
    print(
        f"Percentage of cases : "
        f"{float(top['percentage_of_all_cases']):.2f}%"
    )
    print(f"Serious cases       : {int(top['serious_cases'])}")
    print(
        f"Serious percentage  : "
        f"{float(top['serious_percentage']):.2f}%"
    )
    print(f"Evidence level      : {top['evidence_level']}")
    print(f"Causality           : {top['causality']}")
    print(
        f"Disproportionality  : "
        f"{top['disproportionality']}"
    )


section("BUILDING PHASE 8 EXECUTIVE SUMMARY")

top = cards_df.sort_values("rank").iloc[0]

executive = pd.DataFrame([{
    "integrated_cases":
        int(summary_row["integrated_cases"]),

    "bisoprolol_cases":
        int(summary_row["bisoprolol_cases"]),

    "candidate_reactions":
        int(summary_row["candidate_reactions"]),

    "candidate_case_reaction_rows":
        int(summary_row["candidate_case_reaction_rows"]),

    "candidate_unique_cases":
        int(summary_row["candidate_unique_cases"]),

    "unique_raw_reaction_terms":
        int(summary_row["unique_raw_reaction_terms"]),

    "top_candidate":
        top["reaction"],

    "top_candidate_cases":
        int(top["reported_cases"]),

    "top_candidate_percentage":
        float(top["percentage_of_all_cases"]),

    "top_candidate_serious_cases":
        int(top["serious_cases"]),

    "comparator_available":
        False,

    "ror_available":
        False,

    "prr_available":
        False,

    "frequency_is_incidence":
        False,

    "causality_established":
        False,

    "disproportionality_established":
        False,

    "co_medication_interaction_established":
        False,

    "analysis_type":
        "Descriptive exploratory pharmacovigilance reporting",

    "reporting_scope":
        "Bisoprolol-containing ICSR cases",

    "interpretation":
        (
            "Candidate reactions represent reported case "
            "patterns and require further investigation."
        ),

    "major_limitation":
        (
            "No internal non-Bisoprolol comparator cohort "
            "is available."
        ),
}])

executive.to_csv(
    path("phase8_analysis_summary.csv"),
    index=False
)

print(
    "PASS - Executive summary created:\n"
    + path("phase8_analysis_summary.csv")
)


section("PHASE 8 ANALYSIS RESULT")

print(f"Integrated cases       : {int(summary_row['integrated_cases']):,}")
print(f"Bisoprolol cases       : {int(summary_row['bisoprolol_cases']):,}")
print(f"Candidate reactions    : {int(summary_row['candidate_reactions'])}")
print(
    f"Candidate case rows   : "
    f"{int(summary_row['candidate_case_reaction_rows'])}"
)
print(
    f"Candidate unique cases: "
    f"{int(summary_row['candidate_unique_cases'])}"
)
print(
    f"Unique raw reactions  : "
    f"{int(summary_row['unique_raw_reaction_terms'])}"
)

print()
print(f"TOP CANDIDATE: {top['reaction']}")
print(f"Cases          : {int(top['reported_cases'])}")
print(
    f"Percentage     : "
    f"{float(top['percentage_of_all_cases']):.2f}%"
)
print(f"Serious cases  : {int(top['serious_cases'])}")
print(
    f"Serious %      : "
    f"{float(top['serious_percentage']):.2f}%"
)

section("ANALYTICAL SAFETY")

print("Comparator cohort available              : NO")
print("ROR calculated                            : NO")
print("PRR calculated                            : NO")
print("Frequency interpreted as incidence       : NO")
print("Causality established                    : NO")
print("Disproportionality established           : NO")
print("Co-medication interaction established    : NO")

print("""
Phase 8 remains descriptive and exploratory.

The generated reporting layer summarizes reported case patterns
without interpreting them as incidence, causality,
disproportionality, or confirmed drug-drug interactions.

No artificial comparator cohort has been created.
""")

print("=" * 100)
print("PHASE 8 ANALYSIS COMPLETE")
print("=" * 100)

print("""
Generated files:
 - phase8_structured_reporting.csv
 - phase8_candidate_report_cards.csv
 - phase8_analysis_summary.csv

Proceed to Phase 8 validation.
""")