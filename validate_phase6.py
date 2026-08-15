import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

FILES = {
    "phase6_candidate_profiles.csv": [
        "reactionmeddrapt",
        "case_count",
        "percentage_of_all_cases",
        "serious_case_count",
        "serious_percentage",
    ],
    "phase6_candidate_demographics.csv": [
        "reactionmeddrapt",
        "dimension",
        "category",
        "case_count",
        "percentage_within_candidate",
    ],
    "phase6_candidate_countries.csv": [
        "reactionmeddrapt",
        "country",
        "case_count",
        "percentage_within_candidate",
    ],
    "phase6_candidate_products.csv": [
        "reactionmeddrapt",
        "product",
        "case_count",
        "percentage_within_candidate",
    ],
    "phase6_analysis_summary.csv": [
        "integrated_cases",
        "bisoprolol_cases",
        "candidate_reactions",
        "comparator_available",
        "ror_available",
        "prr_available",
        "causality_established",
        "disproportionality_established",
    ],
}


def section(title):
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


print("=" * 90)
print("PHASE 6 - SIGNAL ANALYSIS VALIDATION")
print("=" * 90)


# ======================================================================
# FILE CHECK
# ======================================================================

section("FILE CHECK")

loaded = {}

for filename in FILES:

    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        print(f"FAIL - {filename}")
        raise SystemExit(1)

    print(f"PASS - {filename}")

    loaded[filename] = pd.read_csv(path)


# ======================================================================
# COLUMN VALIDATION
# ======================================================================

section("COLUMN VALIDATION")

for filename, required_columns in FILES.items():

    df = loaded[filename]

    for column in required_columns:

        if column not in df.columns:
            print(
                f"FAIL - {filename}: missing {column}"
            )
            raise SystemExit(1)

        print(
            f"PASS - {filename}: {column}"
        )


# ======================================================================
# PROFILE VALIDATION
# ======================================================================

section("CANDIDATE PROFILE VALIDATION")

profiles = loaded["phase6_candidate_profiles.csv"]

if profiles.empty:
    print("FAIL - Candidate profiles are empty")
    raise SystemExit(1)

if profiles["reactionmeddrapt"].duplicated().any():
    print("FAIL - Duplicate candidate reactions")
    raise SystemExit(1)

if (profiles["case_count"] < 0).any():
    print("FAIL - Negative case counts")
    raise SystemExit(1)

if (
    (profiles["percentage_of_all_cases"] < 0)
    | (profiles["percentage_of_all_cases"] > 100)
).any():
    print("FAIL - Invalid percentages")
    raise SystemExit(1)

print(f"PASS - Candidate profiles: {len(profiles)}")


# ======================================================================
# DEMOGRAPHIC VALIDATION
# ======================================================================

section("DEMOGRAPHIC VALIDATION")

demographics = loaded[
    "phase6_candidate_demographics.csv"
]

if demographics.empty:
    print("FAIL - Demographic dataset is empty")
    raise SystemExit(1)

if (
    demographics["case_count"] < 0
).any():
    print("FAIL - Negative demographic counts")
    raise SystemExit(1)

print(
    f"PASS - Demographic rows: {len(demographics):,}"
)


# ======================================================================
# COUNTRY VALIDATION
# ======================================================================

section("COUNTRY VALIDATION")

countries = loaded[
    "phase6_candidate_countries.csv"
]

if countries.empty:
    print("FAIL - Country dataset is empty")
    raise SystemExit(1)

print(
    f"PASS - Country rows: {len(countries):,}"
)


# ======================================================================
# PRODUCT VALIDATION
# ======================================================================

section("PRODUCT PATTERN VALIDATION")

products = loaded[
    "phase6_candidate_products.csv"
]

if products.empty:
    print("FAIL - Product dataset is empty")
    raise SystemExit(1)

print(
    f"PASS - Product rows: {len(products):,}"
)


# ======================================================================
# SUMMARY VALIDATION
# ======================================================================

section("SUMMARY VALIDATION")

summary = loaded[
    "phase6_analysis_summary.csv"
]

if len(summary) != 1:
    print("FAIL - Summary must contain exactly one row")
    raise SystemExit(1)

row = summary.iloc[0]

if bool(row["comparator_available"]):
    print("FAIL - Comparator incorrectly marked available")
    raise SystemExit(1)

if bool(row["ror_available"]):
    print("FAIL - ROR incorrectly marked available")
    raise SystemExit(1)

if bool(row["prr_available"]):
    print("FAIL - PRR incorrectly marked available")
    raise SystemExit(1)

if bool(row["causality_established"]):
    print("FAIL - Causality incorrectly marked established")
    raise SystemExit(1)

if bool(row["disproportionality_established"]):
    print(
        "FAIL - Disproportionality incorrectly marked established"
    )
    raise SystemExit(1)

print("PASS - Comparator unavailable as expected")
print("PASS - ROR not calculated")
print("PASS - PRR not calculated")
print("PASS - Causality not established")
print("PASS - Disproportionality not established")


# ======================================================================
# CASE COUNT VALIDATION
# ======================================================================

section("CASE COUNT VALIDATION")

integrated_file = os.path.join(
    DATA_DIR,
    "integrated_icsr_cases.csv"
)

if not os.path.exists(integrated_file):
    print("FAIL - integrated_icsr_cases.csv missing")
    raise SystemExit(1)

integrated = pd.read_csv(integrated_file)

expected_cases = len(integrated)

if int(row["integrated_cases"]) != expected_cases:
    print("FAIL - Integrated case count mismatch")
    raise SystemExit(1)

if int(row["bisoprolol_cases"]) != expected_cases:
    print("FAIL - Bisoprolol case count mismatch")
    raise SystemExit(1)

print(
    f"PASS - Integrated cases: {expected_cases:,}"
)

print(
    f"PASS - Bisoprolol cases: "
    f"{int(row['bisoprolol_cases']):,}"
)


# ======================================================================
# FINAL RESULT
# ======================================================================

section("FINAL RESULT")

print("PASS")
print()
print("Phase 6 signal analysis is structurally valid.")
print()
print("Phase status:")
print("Phase 1 - Drug normalization       : COMPLETE")
print("Phase 2 - Reaction normalization   : COMPLETE")
print("Phase 3 - Structure validation     : COMPLETE")
print("Phase 4 - Case integration         : COMPLETE")
print("Phase 5 - Pharmacovigilance screen : COMPLETE")
print("Phase 6 - Signal pattern analysis  : COMPLETE")
print()
print("IMPORTANT:")
print("No internal non-Bisoprolol comparator exists.")
print("ROR/PRR must not be calculated.")
print("Findings remain descriptive/exploratory.")
print("No causal conclusion is established.")

print("=" * 90)