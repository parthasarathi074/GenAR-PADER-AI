import os
import sys
import pandas as pd
import numpy as np


# =============================================================================
# PHASE 7 - SIGNAL EVIDENCE & REPORTING ANALYSIS
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def subsection(title):
    print("\n" + "-" * 100)
    print(title)
    print("-" * 100)


def require_file(filename):
    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        print(f"FAIL - Missing file: {filename}")
        sys.exit(1)

    print(f"PASS - {filename}")
    return path


def normalize_text(series):
    return (
        series.fillna("[MISSING]")
        .astype(str)
        .str.strip()
        .replace("", "[MISSING]")
    )


def safe_numeric(series):
    return pd.to_numeric(series, errors="coerce")


def age_group(age):
    if pd.isna(age):
        return "[MISSING]"
    if age < 18:
        return "0-17"
    if age <= 44:
        return "18-44"
    if age <= 64:
        return "45-64"
    if age <= 74:
        return "65-74"
    if age <= 84:
        return "75-84"
    return "85+"


# =============================================================================
# START
# =============================================================================

section("PHASE 7 - SIGNAL EVIDENCE & REPORTING ANALYSIS")


# =============================================================================
# FILE CHECK
# =============================================================================

section("FILE CHECK")

required_files = [
    "phase6_candidate_profiles.csv",
    "phase6_candidate_demographics.csv",
    "phase6_candidate_countries.csv",
    "phase6_candidate_products.csv",
    "phase6_analysis_summary.csv",
]

paths = {}

for filename in required_files:
    paths[filename] = require_file(filename)


# =============================================================================
# LOAD DATA
# =============================================================================

section("LOADING PHASE 6 OUTPUTS")

profiles = pd.read_csv(paths["phase6_candidate_profiles.csv"])
demographics = pd.read_csv(paths["phase6_candidate_demographics.csv"])
countries = pd.read_csv(paths["phase6_candidate_countries.csv"])
products = pd.read_csv(paths["phase6_candidate_products.csv"])
phase6_summary = pd.read_csv(paths["phase6_analysis_summary.csv"])

print(f"Candidate profiles : {len(profiles):,}")
print(f"Demographic rows   : {len(demographics):,}")
print(f"Country rows       : {len(countries):,}")
print(f"Product rows       : {len(products):,}")
print(f"Summary rows       : {len(phase6_summary):,}")


# =============================================================================
# COLUMN VALIDATION
# =============================================================================

section("COLUMN VALIDATION")

required_profile_columns = [
    "reactionmeddrapt",
    "case_count",
    "percentage_of_all_cases",
    "serious_case_count",
    "serious_percentage",
    "death_case_count",
    "life_threatening_case_count",
    "hospitalization_case_count",
    "disabling_case_count",
    "female_cases",
    "male_cases",
    "missing_sex_cases",
    "mean_age",
    "median_age",
    "minimum_age",
    "maximum_age",
]

required_demo_columns = [
    "reactionmeddrapt",
    "dimension",
    "category",
    "case_count",
    "percentage_within_candidate",
]

required_country_columns = [
    "reactionmeddrapt",
    "country",
    "case_count",
    "percentage_within_candidate",
]

required_product_columns = [
    "reactionmeddrapt",
    "product",
    "case_count",
    "percentage_within_candidate",
]

required_summary_columns = [
    "integrated_cases",
    "bisoprolol_cases",
    "candidate_reactions",
    "candidate_case_reaction_rows",
    "candidate_unique_cases",
    "unique_raw_reaction_terms",
    "comparator_available",
    "ror_available",
    "prr_available",
    "analysis_type",
    "causality_established",
    "disproportionality_established",
]


def validate_columns(df, required, label):
    for column in required:
        if column in df.columns:
            print(f"PASS - {label}: {column}")
        else:
            print(f"FAIL - {label}: {column}")
            sys.exit(1)


validate_columns(profiles, required_profile_columns, "profiles")
validate_columns(demographics, required_demo_columns, "demographics")
validate_columns(countries, required_country_columns, "countries")
validate_columns(products, required_product_columns, "products")
validate_columns(phase6_summary, required_summary_columns, "summary")


# =============================================================================
# ANALYTICAL SAFETY CHECK
# =============================================================================

section("ANALYTICAL SAFETY CHECK")

summary_row = phase6_summary.iloc[0]

comparator_available = bool(summary_row["comparator_available"])
ror_available = bool(summary_row["ror_available"])
prr_available = bool(summary_row["prr_available"])
causality_established = bool(summary_row["causality_established"])
disproportionality_established = bool(
    summary_row["disproportionality_established"]
)

print(f"Comparator available : {comparator_available}")
print(f"ROR available        : {ror_available}")
print(f"PRR available        : {prr_available}")
print(f"Causality established: {causality_established}")
print(f"Disproportionality   : {disproportionality_established}")

if comparator_available:
    print("WARNING - Comparator exists. Review before proceeding.")
else:
    print("PASS - No internal comparator detected.")

if ror_available:
    print("FAIL - ROR unexpectedly marked available.")
    sys.exit(1)
else:
    print("PASS - ROR unavailable.")

if prr_available:
    print("FAIL - PRR unexpectedly marked available.")
    sys.exit(1)
else:
    print("PASS - PRR unavailable.")

if causality_established:
    print("FAIL - Causality must not be established in this phase.")
    sys.exit(1)
else:
    print("PASS - Causality remains unestablished.")

if disproportionality_established:
    print("FAIL - Disproportionality must not be established.")
    sys.exit(1)
else:
    print("PASS - Disproportionality remains unestablished.")


# =============================================================================
# CANDIDATE EVIDENCE TABLE
# =============================================================================

section("BUILDING CANDIDATE EVIDENCE TABLE")

evidence = profiles.copy()

evidence["case_count"] = pd.to_numeric(
    evidence["case_count"], errors="coerce"
).fillna(0).astype(int)

evidence["serious_case_count"] = pd.to_numeric(
    evidence["serious_case_count"], errors="coerce"
).fillna(0).astype(int)

evidence["death_case_count"] = pd.to_numeric(
    evidence["death_case_count"], errors="coerce"
).fillna(0).astype(int)

evidence["life_threatening_case_count"] = pd.to_numeric(
    evidence["life_threatening_case_count"], errors="coerce"
).fillna(0).astype(int)

evidence["hospitalization_case_count"] = pd.to_numeric(
    evidence["hospitalization_case_count"], errors="coerce"
).fillna(0).astype(int)

evidence["disabling_case_count"] = pd.to_numeric(
    evidence["disabling_case_count"], errors="coerce"
).fillna(0).astype(int)

evidence["percentage_of_all_cases"] = pd.to_numeric(
    evidence["percentage_of_all_cases"], errors="coerce"
).fillna(0)

evidence["serious_percentage"] = pd.to_numeric(
    evidence["serious_percentage"], errors="coerce"
).fillna(0)

evidence["mean_age"] = pd.to_numeric(
    evidence["mean_age"], errors="coerce"
)

evidence["median_age"] = pd.to_numeric(
    evidence["median_age"], errors="coerce"
)

evidence["minimum_age"] = pd.to_numeric(
    evidence["minimum_age"], errors="coerce"
)

evidence["maximum_age"] = pd.to_numeric(
    evidence["maximum_age"], errors="coerce"
)

evidence["analysis_type"] = "descriptive_exploratory"
evidence["frequency_is_incidence"] = False
evidence["causality_established"] = False
evidence["disproportionality_available"] = False
evidence["comparator_available"] = False

evidence["evidence_level"] = np.where(
    evidence["case_count"] >= 20,
    "higher_frequency_candidate",
    np.where(
        evidence["case_count"] >= 10,
        "moderate_frequency_candidate",
        "lower_frequency_candidate"
    )
)

evidence = evidence[
    [
        "reactionmeddrapt",
        "case_count",
        "percentage_of_all_cases",
        "serious_case_count",
        "serious_percentage",
        "death_case_count",
        "life_threatening_case_count",
        "hospitalization_case_count",
        "disabling_case_count",
        "female_cases",
        "male_cases",
        "missing_sex_cases",
        "mean_age",
        "median_age",
        "minimum_age",
        "maximum_age",
        "evidence_level",
        "analysis_type",
        "frequency_is_incidence",
        "comparator_available",
        "disproportionality_available",
        "causality_established",
    ]
]

evidence = evidence.sort_values(
    by=["case_count", "serious_case_count"],
    ascending=[False, False]
)

evidence_path = os.path.join(
    DATA_DIR,
    "phase7_candidate_evidence.csv"
)

evidence.to_csv(evidence_path, index=False)

print(f"PASS - Candidate evidence dataset created:")
print(evidence_path)


# =============================================================================
# EVIDENCE RANKING
# =============================================================================

section("CANDIDATE EVIDENCE RANKING")

ranking = evidence[
    [
        "reactionmeddrapt",
        "case_count",
        "percentage_of_all_cases",
        "serious_case_count",
        "serious_percentage",
        "death_case_count",
        "hospitalization_case_count",
        "mean_age",
        "median_age",
        "evidence_level",
    ]
].copy()

ranking.insert(
    0,
    "rank",
    range(1, len(ranking) + 1)
)

ranking_path = os.path.join(
    DATA_DIR,
    "phase7_candidate_ranking.csv"
)

ranking.to_csv(ranking_path, index=False)

print(f"PASS - Candidate ranking created:")
print(ranking_path)

print("\nTOP CANDIDATES")
print("-" * 100)

for _, row in ranking.iterrows():
    print(
        f"{int(row['rank']):02d}. "
        f"{row['reactionmeddrapt']:<35} "
        f"cases={int(row['case_count']):3d} "
        f"serious={int(row['serious_case_count']):3d} "
        f"serious%={row['serious_percentage']:.2f}% "
        f"level={row['evidence_level']}"
    )


# =============================================================================
# SERIOUSNESS EVIDENCE
# =============================================================================

section("SERIOUSNESS EVIDENCE")

seriousness_rows = []

for _, row in evidence.iterrows():

    total = row["case_count"]

    if total == 0:
        continue

    seriousness_rows.append({
        "reactionmeddrapt": row["reactionmeddrapt"],
        "case_count": int(total),
        "serious_case_count": int(row["serious_case_count"]),
        "serious_percentage": round(
            row["serious_case_count"] / total * 100,
            2
        ),
        "death_case_count": int(row["death_case_count"]),
        "death_percentage": round(
            row["death_case_count"] / total * 100,
            2
        ),
        "life_threatening_case_count": int(
            row["life_threatening_case_count"]
        ),
        "life_threatening_percentage": round(
            row["life_threatening_case_count"] / total * 100,
            2
        ),
        "hospitalization_case_count": int(
            row["hospitalization_case_count"]
        ),
        "hospitalization_percentage": round(
            row["hospitalization_case_count"] / total * 100,
            2
        ),
        "disabling_case_count": int(
            row["disabling_case_count"]
        ),
        "disabling_percentage": round(
            row["disabling_case_count"] / total * 100,
            2
        ),
    })

seriousness_df = pd.DataFrame(seriousness_rows)

seriousness_path = os.path.join(
    DATA_DIR,
    "phase7_candidate_seriousness.csv"
)

seriousness_df.to_csv(
    seriousness_path,
    index=False
)

print("PASS - Candidate seriousness evidence created:")
print(seriousness_path)


# =============================================================================
# DEMOGRAPHIC EVIDENCE
# =============================================================================

section("DEMOGRAPHIC EVIDENCE")

demo = demographics.copy()

demo["category"] = normalize_text(demo["category"])

demo["case_count"] = pd.to_numeric(
    demo["case_count"], errors="coerce"
).fillna(0).astype(int)

demo["percentage_within_candidate"] = pd.to_numeric(
    demo["percentage_within_candidate"],
    errors="coerce"
).fillna(0)

demo["analysis_type"] = "descriptive_exploratory"

demo["interpretation_allowed"] = False

demo_path = os.path.join(
    DATA_DIR,
    "phase7_candidate_demographics.csv"
)

demo.to_csv(
    demo_path,
    index=False
)

print("PASS - Candidate demographic evidence created:")
print(demo_path)


# =============================================================================
# COUNTRY EVIDENCE
# =============================================================================

section("COUNTRY EVIDENCE")

country = countries.copy()

country["country"] = normalize_text(country["country"])

country["case_count"] = pd.to_numeric(
    country["case_count"], errors="coerce"
).fillna(0).astype(int)

country["percentage_within_candidate"] = pd.to_numeric(
    country["percentage_within_candidate"],
    errors="coerce"
).fillna(0)

country["analysis_type"] = "descriptive_exploratory"

country["geographic_causality_inferred"] = False

country_path = os.path.join(
    DATA_DIR,
    "phase7_candidate_countries.csv"
)

country.to_csv(
    country_path,
    index=False
)

print("PASS - Candidate country evidence created:")
print(country_path)


# =============================================================================
# CO-MEDICATION EVIDENCE
# =============================================================================

section("CO-MEDICATION EVIDENCE")

product = products.copy()

product["product"] = normalize_text(product["product"])

product["case_count"] = pd.to_numeric(
    product["case_count"], errors="coerce"
).fillna(0).astype(int)

product["percentage_within_candidate"] = pd.to_numeric(
    product["percentage_within_candidate"],
    errors="coerce"
).fillna(0)

product["analysis_type"] = "descriptive_exploratory"

product["interaction_established"] = False

product_path = os.path.join(
    DATA_DIR,
    "phase7_candidate_products.csv"
)

product.to_csv(
    product_path,
    index=False
)

print("PASS - Candidate co-medication evidence created:")
print(product_path)


# =============================================================================
# REPORTING MATRIX
# =============================================================================

section("BUILDING STRUCTURED REPORTING MATRIX")

reporting_rows = []

for _, row in evidence.iterrows():

    reporting_rows.append({
        "reactionmeddrapt": row["reactionmeddrapt"],
        "reported_cases": int(row["case_count"]),
        "percentage_of_all_cases": round(
            row["percentage_of_all_cases"],
            2
        ),
        "serious_cases": int(row["serious_case_count"]),
        "serious_percentage": round(
            row["serious_percentage"],
            2
        ),
        "death_cases": int(row["death_case_count"]),
        "hospitalization_cases": int(
            row["hospitalization_case_count"]
        ),
        "mean_age": row["mean_age"],
        "median_age": row["median_age"],
        "evidence_level": row["evidence_level"],
        "analysis_type": "descriptive_exploratory",
        "frequency_interpretation": "reported_case_frequency_only",
        "causality_status": "not_established",
        "disproportionality_status": "not_available",
        "comparator_status": "not_available",
        "interaction_status": "not_established",
    })

reporting = pd.DataFrame(reporting_rows)

reporting_path = os.path.join(
    DATA_DIR,
    "phase7_reporting_matrix.csv"
)

reporting.to_csv(
    reporting_path,
    index=False
)

print("PASS - Structured reporting matrix created:")
print(reporting_path)


# =============================================================================
# EXECUTIVE SUMMARY
# =============================================================================

section("BUILDING PHASE 7 EXECUTIVE SUMMARY")

integrated_cases = int(summary_row["integrated_cases"])
bisoprolol_cases = int(summary_row["bisoprolol_cases"])
candidate_reactions = int(summary_row["candidate_reactions"])
candidate_rows = int(summary_row["candidate_case_reaction_rows"])
candidate_unique_cases = int(summary_row["candidate_unique_cases"])
unique_reactions = int(summary_row["unique_raw_reaction_terms"])

top_candidate = evidence.iloc[0]

executive_summary = pd.DataFrame([
    {
        "integrated_cases": integrated_cases,
        "bisoprolol_cases": bisoprolol_cases,
        "candidate_reactions": candidate_reactions,
        "candidate_case_reaction_rows": candidate_rows,
        "candidate_unique_cases": candidate_unique_cases,
        "unique_raw_reaction_terms": unique_reactions,
        "top_candidate": top_candidate["reactionmeddrapt"],
        "top_candidate_cases": int(top_candidate["case_count"]),
        "top_candidate_percentage": round(
            top_candidate["percentage_of_all_cases"],
            2
        ),
        "top_candidate_serious_cases": int(
            top_candidate["serious_case_count"]
        ),
        "comparator_available": False,
        "ror_available": False,
        "prr_available": False,
        "analysis_type": "descriptive_exploratory",
        "frequency_is_incidence": False,
        "causality_established": False,
        "disproportionality_established": False,
        "co_medication_interaction_established": False,
    }
])

summary_path = os.path.join(
    DATA_DIR,
    "phase7_analysis_summary.csv"
)

executive_summary.to_csv(
    summary_path,
    index=False
)

print("PASS - Phase 7 analysis summary created:")
print(summary_path)


# =============================================================================
# REPORTING PREVIEW
# =============================================================================

section("REPORTING PREVIEW")

print(
    f"Integrated cases       : {integrated_cases:,}"
)
print(
    f"Bisoprolol cases       : {bisoprolol_cases:,}"
)
print(
    f"Candidate reactions    : {candidate_reactions:,}"
)
print(
    f"Candidate case rows    : {candidate_rows:,}"
)
print(
    f"Candidate unique cases : {candidate_unique_cases:,}"
)
print(
    f"Unique raw reactions   : {unique_reactions:,}"
)

print("\nTOP CANDIDATE")

print(
    f"Reaction       : {top_candidate['reactionmeddrapt']}"
)
print(
    f"Cases          : {int(top_candidate['case_count'])}"
)
print(
    f"Percentage     : {top_candidate['percentage_of_all_cases']:.2f}%"
)
print(
    f"Serious cases  : {int(top_candidate['serious_case_count'])}"
)
print(
    f"Serious %      : {top_candidate['serious_percentage']:.2f}%"
)


# =============================================================================
# FINAL SAFETY STATEMENT
# =============================================================================

section("PHASE 7 ANALYTICAL SAFETY")

print("Comparator cohort available : NO")
print("ROR calculated              : NO")
print("PRR calculated              : NO")
print("Causality established       : NO")
print("Disproportionality          : NO")
print("Frequency interpreted as incidence : NO")
print("Co-medication interaction established : NO")

print()
print(
    "Phase 7 remains descriptive and exploratory."
)
print(
    "Candidate reactions represent reported case patterns only."
)
print(
    "The analysis does not establish causality, incidence, "
    "disproportionality, or drug-drug interaction."
)


# =============================================================================
# COMPLETE
# =============================================================================

section("PHASE 7 ANALYSIS COMPLETE")

print("Generated files:")
print(" - phase7_candidate_evidence.csv")
print(" - phase7_candidate_ranking.csv")
print(" - phase7_candidate_seriousness.csv")
print(" - phase7_candidate_demographics.csv")
print(" - phase7_candidate_countries.csv")
print(" - phase7_candidate_products.csv")
print(" - phase7_reporting_matrix.csv")
print(" - phase7_analysis_summary.csv")

print()
print("Phase 7 evidence and reporting analysis is COMPLETE.")
print("Proceed to Phase 7 validation.")