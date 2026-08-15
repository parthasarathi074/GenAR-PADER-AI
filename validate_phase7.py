import os
import sys
import pandas as pd


# =============================================================================
# PHASE 7 - SIGNAL EVIDENCE & REPORTING VALIDATION
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


def check_columns(df, required, label):
    for column in required:
        if column in df.columns:
            print(f"PASS - {label}: {column}")
        else:
            print(f"FAIL - {label}: {column}")
            sys.exit(1)


# =============================================================================
# START
# =============================================================================

section("PHASE 7 - SIGNAL EVIDENCE & REPORTING VALIDATION")


# =============================================================================
# FILE CHECK
# =============================================================================

section("FILE CHECK")

required_files = [
    "phase7_candidate_evidence.csv",
    "phase7_candidate_ranking.csv",
    "phase7_candidate_seriousness.csv",
    "phase7_candidate_demographics.csv",
    "phase7_candidate_countries.csv",
    "phase7_candidate_products.csv",
    "phase7_reporting_matrix.csv",
    "phase7_analysis_summary.csv",
]

paths = {}

for filename in required_files:
    paths[filename] = require_file(filename)


# =============================================================================
# LOAD
# =============================================================================

section("LOADING PHASE 7 OUTPUTS")

evidence = pd.read_csv(
    paths["phase7_candidate_evidence.csv"]
)

ranking = pd.read_csv(
    paths["phase7_candidate_ranking.csv"]
)

seriousness = pd.read_csv(
    paths["phase7_candidate_seriousness.csv"]
)

demographics = pd.read_csv(
    paths["phase7_candidate_demographics.csv"]
)

countries = pd.read_csv(
    paths["phase7_candidate_countries.csv"]
)

products = pd.read_csv(
    paths["phase7_candidate_products.csv"]
)

reporting = pd.read_csv(
    paths["phase7_reporting_matrix.csv"]
)

summary = pd.read_csv(
    paths["phase7_analysis_summary.csv"]
)

print(f"Evidence rows      : {len(evidence):,}")
print(f"Ranking rows       : {len(ranking):,}")
print(f"Seriousness rows   : {len(seriousness):,}")
print(f"Demographic rows   : {len(demographics):,}")
print(f"Country rows       : {len(countries):,}")
print(f"Product rows       : {len(products):,}")
print(f"Reporting rows     : {len(reporting):,}")
print(f"Summary rows       : {len(summary):,}")


# =============================================================================
# COLUMN VALIDATION
# =============================================================================

section("COLUMN VALIDATION")

required_evidence = [
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
]

required_ranking = [
    "rank",
    "reactionmeddrapt",
    "case_count",
    "percentage_of_all_cases",
    "serious_case_count",
    "serious_percentage",
    "evidence_level",
]

required_seriousness = [
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
]

required_demographics = [
    "reactionmeddrapt",
    "dimension",
    "category",
    "case_count",
    "percentage_within_candidate",
    "analysis_type",
    "interpretation_allowed",
]

required_countries = [
    "reactionmeddrapt",
    "country",
    "case_count",
    "percentage_within_candidate",
    "analysis_type",
    "geographic_causality_inferred",
]

required_products = [
    "reactionmeddrapt",
    "product",
    "case_count",
    "percentage_within_candidate",
    "analysis_type",
    "interaction_established",
]

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
    "analysis_type",
    "frequency_is_incidence",
    "causality_established",
    "disproportionality_established",
    "co_medication_interaction_established",
]


check_columns(
    evidence,
    required_evidence,
    "evidence"
)

check_columns(
    ranking,
    required_ranking,
    "ranking"
)

check_columns(
    seriousness,
    required_seriousness,
    "seriousness"
)

check_columns(
    demographics,
    required_demographics,
    "demographics"
)

check_columns(
    countries,
    required_countries,
    "countries"
)

check_columns(
    products,
    required_products,
    "products"
)

check_columns(
    reporting,
    required_reporting,
    "reporting"
)

check_columns(
    summary,
    required_summary,
    "summary"
)


# =============================================================================
# CANDIDATE COUNT VALIDATION
# =============================================================================

section("CANDIDATE COUNT VALIDATION")

candidate_count = len(evidence)

print(f"Candidate evidence rows : {candidate_count}")

if candidate_count == 0:
    print("FAIL - No candidate evidence records.")
    sys.exit(1)

print("PASS - Candidate evidence records exist.")


if len(ranking) != candidate_count:
    print("FAIL - Ranking count does not match evidence count.")
    sys.exit(1)

print("PASS - Ranking count matches evidence count.")


if len(seriousness) != candidate_count:
    print("FAIL - Seriousness count does not match evidence count.")
    sys.exit(1)

print("PASS - Seriousness count matches evidence count.")


if len(reporting) != candidate_count:
    print("FAIL - Reporting matrix count does not match evidence count.")
    sys.exit(1)

print("PASS - Reporting matrix count matches evidence count.")


# =============================================================================
# DUPLICATE CANDIDATE CHECK
# =============================================================================

section("DUPLICATE CANDIDATE CHECK")

duplicate_candidates = evidence[
    evidence["reactionmeddrapt"].duplicated()
]

print(
    f"Duplicate candidate reactions : "
    f"{len(duplicate_candidates)}"
)

if len(duplicate_candidates) > 0:
    print("FAIL - Duplicate candidate reactions detected.")
    sys.exit(1)

print("PASS - Candidate reactions are unique.")


# =============================================================================
# RANKING VALIDATION
# =============================================================================

section("RANKING VALIDATION")

expected_ranks = list(range(1, candidate_count + 1))

actual_ranks = (
    pd.to_numeric(
        ranking["rank"],
        errors="coerce"
    )
    .dropna()
    .astype(int)
    .tolist()
)

if actual_ranks != expected_ranks:
    print("FAIL - Ranking sequence is not contiguous.")
    sys.exit(1)

print("PASS - Ranking sequence is contiguous.")


ranking_cases = pd.to_numeric(
    ranking["case_count"],
    errors="coerce"
)

if ranking_cases.isna().any():
    print("FAIL - Missing ranking case counts.")
    sys.exit(1)

if (ranking_cases < 0).any():
    print("FAIL - Negative case count detected.")
    sys.exit(1)

print("PASS - Ranking case counts valid.")


# =============================================================================
# EVIDENCE LEVEL VALIDATION
# =============================================================================

section("EVIDENCE LEVEL VALIDATION")

valid_levels = {
    "higher_frequency_candidate",
    "moderate_frequency_candidate",
    "lower_frequency_candidate",
}

invalid_levels = set(
    evidence["evidence_level"].dropna().unique()
) - valid_levels

if invalid_levels:
    print(
        "FAIL - Invalid evidence levels:",
        sorted(invalid_levels)
    )
    sys.exit(1)

print("PASS - Evidence levels are valid.")


# =============================================================================
# PERCENTAGE VALIDATION
# =============================================================================

section("PERCENTAGE VALIDATION")

percentage_columns = [
    (
        evidence,
        "percentage_of_all_cases"
    ),
    (
        evidence,
        "serious_percentage"
    ),
    (
        demographics,
        "percentage_within_candidate"
    ),
    (
        countries,
        "percentage_within_candidate"
    ),
    (
        products,
        "percentage_within_candidate"
    ),
    (
        reporting,
        "percentage_of_all_cases"
    ),
    (
        reporting,
        "serious_percentage"
    ),
]

for df, column in percentage_columns:

    values = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    if values.isna().any():
        print(
            f"FAIL - Missing/non-numeric values in {column}"
        )
        sys.exit(1)

    if ((values < 0) | (values > 100)).any():
        print(
            f"FAIL - Invalid percentage values in {column}"
        )
        sys.exit(1)

    print(f"PASS - {column}")


# =============================================================================
# SERIOUSNESS VALIDATION
# =============================================================================

section("SERIOUSNESS VALIDATION")

for _, row in seriousness.iterrows():

    total = int(row["case_count"])

    serious = int(row["serious_case_count"])
    death = int(row["death_case_count"])
    life = int(row["life_threatening_case_count"])
    hospitalization = int(row["hospitalization_case_count"])
    disabling = int(row["disabling_case_count"])

    if serious > total:
        print(
            f"FAIL - Serious cases exceed total for "
            f"{row['reactionmeddrapt']}"
        )
        sys.exit(1)

    if death > total:
        print(
            f"FAIL - Death cases exceed total for "
            f"{row['reactionmeddrapt']}"
        )
        sys.exit(1)

    if life > total:
        print(
            f"FAIL - Life-threatening cases exceed total for "
            f"{row['reactionmeddrapt']}"
        )
        sys.exit(1)

    if hospitalization > total:
        print(
            f"FAIL - Hospitalization cases exceed total for "
            f"{row['reactionmeddrapt']}"
        )
        sys.exit(1)

    if disabling > total:
        print(
            f"FAIL - Disabling cases exceed total for "
            f"{row['reactionmeddrapt']}"
        )
        sys.exit(1)

print("PASS - Seriousness counts are logically valid.")


# =============================================================================
# DEMOGRAPHIC VALIDATION
# =============================================================================

section("DEMOGRAPHIC VALIDATION")

if demographics["reactionmeddrapt"].isna().any():
    print("FAIL - Missing candidate reaction in demographics.")
    sys.exit(1)

if demographics["dimension"].isna().any():
    print("FAIL - Missing demographic dimension.")
    sys.exit(1)

if demographics["category"].isna().any():
    print("FAIL - Missing demographic category.")
    sys.exit(1)

print("PASS - Demographic structure is valid.")

if demographics["interpretation_allowed"].astype(str).str.lower().isin(
    ["true", "1", "yes"]
).any():
    print(
        "FAIL - Demographic interpretation is incorrectly marked allowed."
    )
    sys.exit(1)

print(
    "PASS - Demographic results remain descriptive."
)


# =============================================================================
# COUNTRY VALIDATION
# =============================================================================

section("COUNTRY VALIDATION")

if countries["reactionmeddrapt"].isna().any():
    print("FAIL - Missing candidate reaction in countries.")
    sys.exit(1)

if countries["country"].isna().any():
    print("FAIL - Missing country.")
    sys.exit(1)

country_causality = (
    countries["geographic_causality_inferred"]
    .astype(str)
    .str.lower()
)

if country_causality.isin(
    ["true", "1", "yes"]
).any():
    print(
        "FAIL - Geographic causality incorrectly inferred."
    )
    sys.exit(1)

print(
    "PASS - Country patterns remain descriptive."
)


# =============================================================================
# PRODUCT / INTERACTION VALIDATION
# =============================================================================

section("PRODUCT PATTERN VALIDATION")

if products["reactionmeddrapt"].isna().any():
    print("FAIL - Missing candidate reaction in product data.")
    sys.exit(1)

if products["product"].isna().any():
    print("FAIL - Missing product value.")
    sys.exit(1)

interaction_status = (
    products["interaction_established"]
    .astype(str)
    .str.lower()
)

if interaction_status.isin(
    ["true", "1", "yes"]
).any():
    print(
        "FAIL - Drug interaction incorrectly established."
    )
    sys.exit(1)

print(
    "PASS - Product/co-medication patterns remain descriptive."
)


# =============================================================================
# REPORTING MATRIX VALIDATION
# =============================================================================

section("REPORTING MATRIX VALIDATION")

allowed_frequency_interpretation = {
    "reported_case_frequency_only"
}

invalid_frequency = set(
    reporting["frequency_interpretation"].dropna().unique()
) - allowed_frequency_interpretation

if invalid_frequency:
    print(
        "FAIL - Invalid frequency interpretation:",
        sorted(invalid_frequency)
    )
    sys.exit(1)

print(
    "PASS - Frequency interpretation correctly restricted."
)


allowed_causality = {"not_established"}

if not set(
    reporting["causality_status"].dropna().unique()
).issubset(allowed_causality):

    print(
        "FAIL - Invalid causality status."
    )
    sys.exit(1)

print(
    "PASS - Causality remains unestablished."
)


allowed_disproportionality = {"not_available"}

if not set(
    reporting["disproportionality_status"].dropna().unique()
).issubset(allowed_disproportionality):

    print(
        "FAIL - Invalid disproportionality status."
    )
    sys.exit(1)

print(
    "PASS - Disproportionality remains unavailable."
)


allowed_comparator = {"not_available"}

if not set(
    reporting["comparator_status"].dropna().unique()
).issubset(allowed_comparator):

    print(
        "FAIL - Invalid comparator status."
    )
    sys.exit(1)

print(
    "PASS - Comparator status correctly recorded."
)


allowed_interaction = {"not_established"}

if not set(
    reporting["interaction_status"].dropna().unique()
).issubset(allowed_interaction):

    print(
        "FAIL - Invalid interaction status."
    )
    sys.exit(1)

print(
    "PASS - Interaction status remains unestablished."
)


# =============================================================================
# SUMMARY VALIDATION
# =============================================================================

section("SUMMARY VALIDATION")

if len(summary) != 1:
    print(
        f"FAIL - Expected exactly one summary row, found {len(summary)}"
    )
    sys.exit(1)

summary_row = summary.iloc[0]

integrated_cases = int(
    summary_row["integrated_cases"]
)

bisoprolol_cases = int(
    summary_row["bisoprolol_cases"]
)

candidate_reactions = int(
    summary_row["candidate_reactions"]
)

candidate_unique_cases = int(
    summary_row["candidate_unique_cases"]
)

if integrated_cases != 1024:
    print(
        f"WARNING - Integrated cases = {integrated_cases:,}"
    )
else:
    print("PASS - Integrated cases: 1,024")


if bisoprolol_cases != integrated_cases:
    print(
        "FAIL - Bisoprolol cohort does not cover all integrated cases."
    )
    sys.exit(1)

print(
    "PASS - Bisoprolol cases match integrated cases."
)


if candidate_reactions != len(evidence):
    print(
        "FAIL - Candidate count mismatch."
    )
    sys.exit(1)

print(
    "PASS - Candidate count matches evidence dataset."
)


if candidate_unique_cases < candidate_reactions:
    print(
        "WARNING - Candidate unique case count is lower than candidate count."
    )
else:
    print(
        "PASS - Candidate unique case count is logically consistent."
    )


# =============================================================================
# ANALYTICAL SAFETY
# =============================================================================

section("ANALYTICAL SAFETY VALIDATION")

def check_false_flag(df, column, label):
    values = (
        df[column]
        .astype(str)
        .str.lower()
    )

    if values.isin(
        ["true", "1", "yes"]
    ).any():

        print(
            f"FAIL - {label} incorrectly enabled."
        )
        sys.exit(1)

    print(
        f"PASS - {label} remains disabled."
    )


check_false_flag(
    evidence,
    "frequency_is_incidence",
    "Frequency-as-incidence interpretation"
)

check_false_flag(
    evidence,
    "comparator_available",
    "Comparator availability"
)

check_false_flag(
    evidence,
    "disproportionality_available",
    "Disproportionality availability"
)

check_false_flag(
    evidence,
    "causality_established",
    "Causality"
)

check_false_flag(
    summary,
    "comparator_available",
    "Summary comparator"
)

check_false_flag(
    summary,
    "ror_available",
    "ROR"
)

check_false_flag(
    summary,
    "prr_available",
    "PRR"
)

check_false_flag(
    summary,
    "frequency_is_incidence",
    "Summary incidence interpretation"
)

check_false_flag(
    summary,
    "causality_established",
    "Summary causality"
)

check_false_flag(
    summary,
    "disproportionality_established",
    "Summary disproportionality"
)

check_false_flag(
    summary,
    "co_medication_interaction_established",
    "Co-medication interaction"
)


# =============================================================================
# CANDIDATE CONSISTENCY
# =============================================================================

section("CANDIDATE CONSISTENCY VALIDATION")

evidence_candidates = set(
    evidence["reactionmeddrapt"]
)

ranking_candidates = set(
    ranking["reactionmeddrapt"]
)

seriousness_candidates = set(
    seriousness["reactionmeddrapt"]
)

reporting_candidates = set(
    reporting["reactionmeddrapt"]
)

if evidence_candidates != ranking_candidates:
    print("FAIL - Evidence/ranking candidate mismatch.")
    sys.exit(1)

print("PASS - Evidence and ranking candidates match.")


if evidence_candidates != seriousness_candidates:
    print("FAIL - Evidence/seriousness candidate mismatch.")
    sys.exit(1)

print("PASS - Evidence and seriousness candidates match.")


if evidence_candidates != reporting_candidates:
    print("FAIL - Evidence/reporting candidate mismatch.")
    sys.exit(1)

print("PASS - Evidence and reporting candidates match.")


# =============================================================================
# TOP CANDIDATE VALIDATION
# =============================================================================

section("TOP CANDIDATE VALIDATION")

ranking_sorted = ranking.sort_values(
    by=["case_count", "serious_case_count"],
    ascending=[False, False]
).reset_index(drop=True)

top_ranking_candidate = ranking_sorted.iloc[0]

summary_top_candidate = summary_row["top_candidate"]

if (
    top_ranking_candidate["reactionmeddrapt"]
    != summary_top_candidate
):

    print(
        "FAIL - Summary top candidate does not match ranking."
    )
    sys.exit(1)

print(
    f"PASS - Top candidate: {summary_top_candidate}"
)


if int(
    top_ranking_candidate["case_count"]
) != int(
    summary_row["top_candidate_cases"]
):

    print(
        "FAIL - Top candidate case count mismatch."
    )
    sys.exit(1)

print(
    "PASS - Top candidate case count matches."
)


# =============================================================================
# FINAL RESULT
# =============================================================================

section("FINAL RESULT")

print("PASS")
print()
print("Phase 7 signal evidence and reporting analysis is structurally valid.")
print()
print("Generated datasets:")
print("- phase7_candidate_evidence.csv")
print("- phase7_candidate_ranking.csv")
print("- phase7_candidate_seriousness.csv")
print("- phase7_candidate_demographics.csv")
print("- phase7_candidate_countries.csv")
print("- phase7_candidate_products.csv")
print("- phase7_reporting_matrix.csv")
print("- phase7_analysis_summary.csv")

print()
print("Phase status:")
print("Phase 1 - Drug normalization       : COMPLETE")
print("Phase 2 - Reaction normalization   : COMPLETE")
print("Phase 3 - Structure validation     : COMPLETE")
print("Phase 4 - Case integration         : COMPLETE")
print("Phase 5 - Pharmacovigilance screen : COMPLETE")
print("Phase 6 - Signal pattern analysis  : COMPLETE")
print("Phase 7 - Evidence & reporting     : COMPLETE")

print()
print("IMPORTANT:")
print("No internal non-Bisoprolol comparator exists.")
print("ROR/PRR are not calculated.")
print("Frequency is not interpreted as incidence.")
print("Causality is not established.")
print("Co-medication patterns do not establish interactions.")
print("All findings remain descriptive/exploratory.")

print()
print("=" * 90)