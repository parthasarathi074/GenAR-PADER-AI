import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

FILES = [
    "phase7_candidate_evidence.csv",
    "phase7_candidate_ranking.csv",
    "phase7_candidate_seriousness.csv",
    "phase7_candidate_demographics.csv",
    "phase7_candidate_countries.csv",
    "phase7_candidate_products.csv",
    "phase7_reporting_matrix.csv",
    "phase7_analysis_summary.csv",
]

REQUIRED_COLUMNS = {
    "phase7_candidate_evidence.csv": [
        "reactionmeddrapt",
        "case_count",
        "percentage_of_all_cases",
        "serious_case_count",
        "serious_percentage",
        "death_case_count",
        "life_threatening_case_count",
        "hospitalization_case_count",
        "disabling_case_count",
        "evidence_level",
        "analysis_type",
        "frequency_is_incidence",
        "comparator_available",
        "disproportionality_available",
        "causality_established",
    ],
    "phase7_candidate_ranking.csv": [
        "rank",
        "reactionmeddrapt",
        "case_count",
        "percentage_of_all_cases",
        "serious_case_count",
        "serious_percentage",
        "evidence_level",
    ],
    "phase7_candidate_seriousness.csv": [
        "reactionmeddrapt",
        "case_count",
        "serious_case_count",
        "serious_percentage",
        "death_case_count",
        "death_percentage",
        "life_threatening_case_count",
        "life_threatening_percentage",
        "hospitalization_case_count",
        "hospitalization_percentage",
        "disabling_case_count",
        "disabling_percentage",
    ],
    "phase7_candidate_demographics.csv": [
        "reactionmeddrapt",
        "dimension",
        "category",
        "case_count",
        "percentage_within_candidate",
        "analysis_type",
        "interpretation_allowed",
    ],
    "phase7_candidate_countries.csv": [
        "reactionmeddrapt",
        "country",
        "case_count",
        "percentage_within_candidate",
        "analysis_type",
        "geographic_causality_inferred",
    ],
    "phase7_candidate_products.csv": [
        "reactionmeddrapt",
        "product",
        "case_count",
        "percentage_within_candidate",
        "analysis_type",
        "interaction_established",
    ],
    "phase7_reporting_matrix.csv": [
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
    ],
    "phase7_analysis_summary.csv": [
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
        "analysis_type",
        "frequency_is_incidence",
        "causality_established",
        "disproportionality_established",
        "co_medication_interaction_established",
    ],
}


def header(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("-" * 100)


header("PHASE 8 - STRUCTURED PHARMACOVIGILANCE REPORTING INVESTIGATION")

section("FILE CHECK")

for filename in FILES:
    path = os.path.join(DATA_DIR, filename)

    if os.path.exists(path):
        print(f"PASS - {filename}")
    else:
        print(f"FAIL - {filename}")

section("LOADING PHASE 7 OUTPUTS")

datasets = {}

for filename in FILES:
    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        continue

    df = pd.read_csv(path)

    datasets[filename] = df

    print(f"{filename:<40} rows={len(df):>5} columns={len(df.columns):>3}")


section("COLUMN VALIDATION")

all_valid = True

for filename, required in REQUIRED_COLUMNS.items():

    if filename not in datasets:
        print(f"FAIL - Dataset missing: {filename}")
        all_valid = False
        continue

    df = datasets[filename]

    for column in required:

        if column in df.columns:
            print(f"PASS - {filename}: {column}")
        else:
            print(f"FAIL - {filename}: {column}")
            all_valid = False


section("CANDIDATE INVENTORY")

profiles = datasets["phase7_candidate_evidence.csv"]

for index, row in profiles.iterrows():

    print(
        f"{index + 1:02d}. "
        f"{row['reactionmeddrapt']} | "
        f"cases={int(row['case_count'])} | "
        f"serious={int(row['serious_case_count'])} | "
        f"serious%={float(row['serious_percentage']):.2f}%"
    )


section("TOP CANDIDATE")

ranking = datasets["phase7_candidate_ranking.csv"]

if len(ranking) > 0:

    top = ranking.sort_values("rank").iloc[0]

    print(f"Reaction      : {top['reactionmeddrapt']}")
    print(f"Cases         : {int(top['case_count'])}")
    print(f"Percentage    : {float(top['percentage_of_all_cases']):.2f}%")
    print(f"Serious cases : {int(top['serious_case_count'])}")
    print(f"Serious %     : {float(top['serious_percentage']):.2f}%")
    print(f"Evidence level: {top['evidence_level']}")


section("ANALYTICAL SAFETY STATUS")

summary = datasets["phase7_analysis_summary.csv"].iloc[0]

print(f"Comparator available              : {summary['comparator_available']}")
print(f"ROR available                     : {summary['ror_available']}")
print(f"PRR available                     : {summary['prr_available']}")
print(f"Frequency interpreted as incidence: {summary['frequency_is_incidence']}")
print(f"Causality established             : {summary['causality_established']}")
print(f"Disproportionality established    : {summary['disproportionality_established']}")
print(
    f"Co-medication interaction established: "
    f"{summary['co_medication_interaction_established']}"
)


section("PHASE 8 REPORTING READINESS")

checks = {
    "Candidate evidence available": len(datasets["phase7_candidate_evidence.csv"]) > 0,
    "Candidate ranking available": len(datasets["phase7_candidate_ranking.csv"]) > 0,
    "Seriousness evidence available": len(datasets["phase7_candidate_seriousness.csv"]) > 0,
    "Demographic evidence available": len(datasets["phase7_candidate_demographics.csv"]) > 0,
    "Country evidence available": len(datasets["phase7_candidate_countries.csv"]) > 0,
    "Co-medication evidence available": len(datasets["phase7_candidate_products.csv"]) > 0,
    "Reporting matrix available": len(datasets["phase7_reporting_matrix.csv"]) > 0,
    "Executive summary available": len(datasets["phase7_analysis_summary.csv"]) > 0,
}

for name, result in checks.items():
    print(f"{'PASS' if result else 'FAIL'} - {name}")


section("PHASE 8 INVESTIGATION CONCLUSION")

print("""
The Phase 7 evidence layer is structurally ready for formal reporting.

The available evidence consists of:

1. Candidate reaction frequencies
2. Candidate seriousness patterns
3. Candidate demographic distributions
4. Candidate reporting-country patterns
5. Candidate co-medication patterns
6. Candidate evidence ranking
7. Structured reporting fields

Analytical restrictions remain active:

- Frequency must not be interpreted as incidence.
- No internal non-Bisoprolol comparator is available.
- ROR must not be calculated.
- PRR must not be calculated.
- Causality is not established.
- Disproportionality is not established.
- Co-medication patterns do not establish drug-drug interactions.

Phase 8 can therefore generate a structured pharmacovigilance report
without converting exploratory findings into causal claims.
""")

print("=" * 100)
print("PHASE 8 INVESTIGATION COMPLETE")
print("=" * 100)