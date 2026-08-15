import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

INTEGRATED_FILE = os.path.join(DATA_DIR, "integrated_icsr_cases.csv")
COHORT_FILE = os.path.join(DATA_DIR, "phase5_case_cohort.csv")
REACTIONS_FILE = os.path.join(DATA_DIR, "phase5_case_reactions.csv")
CANDIDATES_FILE = os.path.join(DATA_DIR, "phase5_signal_candidates.csv")

OUT_PROFILE = os.path.join(DATA_DIR, "phase6_candidate_profiles.csv")
OUT_DEMOGRAPHICS = os.path.join(DATA_DIR, "phase6_candidate_demographics.csv")
OUT_COUNTRIES = os.path.join(DATA_DIR, "phase6_candidate_countries.csv")
OUT_PRODUCTS = os.path.join(DATA_DIR, "phase6_candidate_products.csv")
OUT_SUMMARY = os.path.join(DATA_DIR, "phase6_analysis_summary.csv")


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def check_file(path, name):
    if not os.path.exists(path):
        print(f"FAIL - {name} not found:")
        print(path)
        return False

    print(f"PASS - {name}")
    return True


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def is_serious(value):
    return clean_text(value).lower() == "serious"


def split_products(value):
    if pd.isna(value) or not str(value).strip():
        return []

    return [
        x.strip()
        for x in str(value).split(",")
        if x.strip()
    ]


# ======================================================================
# HEADER
# ======================================================================

print("=" * 100)
print("PHASE 6 - SIGNAL ANALYSIS & CLINICAL PATTERN ANALYSIS")
print("=" * 100)


# ======================================================================
# FILE CHECK
# ======================================================================

section("FILE CHECK")

files_ok = (
    check_file(INTEGRATED_FILE, "integrated_icsr_cases.csv")
    and check_file(COHORT_FILE, "phase5_case_cohort.csv")
    and check_file(REACTIONS_FILE, "phase5_case_reactions.csv")
    and check_file(CANDIDATES_FILE, "phase5_signal_candidates.csv")
)

if not files_ok:
    raise SystemExit(1)


# ======================================================================
# LOAD DATA
# ======================================================================

section("LOADING PHASE 6 DATASETS")

integrated = pd.read_csv(INTEGRATED_FILE)
cohort = pd.read_csv(COHORT_FILE)
reactions = pd.read_csv(REACTIONS_FILE)
candidates = pd.read_csv(CANDIDATES_FILE)

print(f"Integrated cases      : {len(integrated):,}")
print(f"Case cohort rows      : {len(cohort):,}")
print(f"Case × reaction rows  : {len(reactions):,}")
print(f"Candidates            : {len(candidates):,}")


# ======================================================================
# REQUIRED COLUMNS
# ======================================================================

section("COLUMN VALIDATION")

required_integrated = [
    "safetyreportid",
    "serious",
    "seriousnessdeath",
    "seriousnesslifethreatening",
    "seriousnesshospitalization",
    "seriousnessdisabling",
    "patient_sex",
    "patient_age",
    "patient_age_unit",
    "primarysourcecountry",
    "occurcountry",
    "reporttype",
    "drug_count",
    "reaction_count",
    "drug_products",
]

required_reactions = [
    "safetyreportid",
    "reaction_index",
    "reactionmeddrapt",
]

required_candidates = [
    "reactionmeddrapt",
    "case_count",
    "percentage_of_cases",
]

for col in required_integrated:
    if col not in integrated.columns:
        raise ValueError(f"Missing integrated column: {col}")

for col in required_reactions:
    if col not in reactions.columns:
        raise ValueError(f"Missing reaction column: {col}")

for col in required_candidates:
    if col not in candidates.columns:
        raise ValueError(f"Missing candidate column: {col}")

print("PASS - Required columns present")


# ======================================================================
# CASE LEVEL VALIDATION
# ======================================================================

section("CASE-LEVEL VALIDATION")

if integrated["safetyreportid"].duplicated().any():
    raise ValueError("Duplicate case IDs in integrated dataset")

if cohort["safetyreportid"].duplicated().any():
    raise ValueError("Duplicate case IDs in cohort")

print("PASS - One row per integrated case")
print("PASS - One row per cohort case")


# ======================================================================
# EXPOSURE CHECK
# ======================================================================

section("BISOPROLOL EXPOSURE")

print(f"Integrated cases : {len(integrated):,}")
print(f"Cohort cases     : {len(cohort):,}")

if len(cohort) != len(integrated):
    raise ValueError("Cohort coverage does not match integrated cases")

print("PASS - Complete Bisoprolol cohort confirmed")


# ======================================================================
# BUILD CASE × CANDIDATE DATA
# ======================================================================

section("BUILDING CANDIDATE CASE DATA")

candidate_names = set(
    candidates["reactionmeddrapt"]
    .dropna()
    .astype(str)
    .str.strip()
)

candidate_reactions = reactions[
    reactions["reactionmeddrapt"]
    .astype(str)
    .str.strip()
    .isin(candidate_names)
].copy()

print(f"Candidate case × reaction rows : {len(candidate_reactions):,}")
print(
    f"Candidate cases                : "
    f"{candidate_reactions['safetyreportid'].nunique():,}"
)


# ======================================================================
# CANDIDATE PROFILE ANALYSIS
# ======================================================================

section("CANDIDATE CLINICAL PROFILES")

profile_rows = []

for reaction_name in sorted(candidate_names):

    reaction_rows = candidate_reactions[
        candidate_reactions["reactionmeddrapt"]
        .astype(str)
        .str.strip()
        == reaction_name
    ]

    case_ids = reaction_rows["safetyreportid"].drop_duplicates()

    case_data = integrated[
        integrated["safetyreportid"].isin(case_ids)
    ].copy()

    case_count = len(case_data)

    serious_count = (
        case_data["serious"]
        .astype(str)
        .str.lower()
        .eq("serious")
        .sum()
    )

    death_count = (
        case_data["seriousnessdeath"]
        .astype(str)
        .str.lower()
        .eq("yes")
        .sum()
    )

    life_threatening_count = (
        case_data["seriousnesslifethreatening"]
        .astype(str)
        .str.lower()
        .eq("yes")
        .sum()
    )

    hospitalization_count = (
        case_data["seriousnesshospitalization"]
        .astype(str)
        .str.lower()
        .eq("yes")
        .sum()
    )

    disabling_count = (
        case_data["seriousnessdisabling"]
        .astype(str)
        .str.lower()
        .eq("yes")
        .sum()
    )

    female_count = (
        case_data["patient_sex"]
        .astype(str)
        .str.lower()
        .eq("female")
        .sum()
    )

    male_count = (
        case_data["patient_sex"]
        .astype(str)
        .str.lower()
        .eq("male")
        .sum()
    )

    valid_age = pd.to_numeric(
        case_data["patient_age"],
        errors="coerce"
    )

    valid_age = valid_age[
        (valid_age >= 0) &
        (valid_age <= 120)
    ]

    profile_rows.append({
        "reactionmeddrapt": reaction_name,
        "case_count": case_count,
        "percentage_of_all_cases": round(
            case_count / len(integrated) * 100, 2
        ),
        "serious_case_count": serious_count,
        "serious_percentage": round(
            serious_count / case_count * 100, 2
        ) if case_count else 0,
        "death_case_count": death_count,
        "life_threatening_case_count": life_threatening_count,
        "hospitalization_case_count": hospitalization_count,
        "disabling_case_count": disabling_count,
        "female_cases": female_count,
        "male_cases": male_count,
        "missing_sex_cases": (
            case_count - female_count - male_count
        ),
        "mean_age": round(valid_age.mean(), 1)
        if len(valid_age) else np.nan,
        "median_age": round(valid_age.median(), 1)
        if len(valid_age) else np.nan,
        "minimum_age": valid_age.min()
        if len(valid_age) else np.nan,
        "maximum_age": valid_age.max()
        if len(valid_age) else np.nan,
    })


profiles = pd.DataFrame(profile_rows)

profiles = profiles.sort_values(
    ["case_count", "serious_percentage"],
    ascending=[False, False]
)

profiles.to_csv(
    OUT_PROFILE,
    index=False
)

print(f"PASS - Candidate profiles created:")
print(OUT_PROFILE)


# ======================================================================
# DEMOGRAPHIC PATTERNS
# ======================================================================

section("CANDIDATE DEMOGRAPHIC PATTERNS")

demographic_rows = []

for reaction_name in sorted(candidate_names):

    case_ids = candidate_reactions[
        candidate_reactions["reactionmeddrapt"]
        .astype(str)
        .str.strip()
        == reaction_name
    ]["safetyreportid"].unique()

    data = integrated[
        integrated["safetyreportid"].isin(case_ids)
    ]

    sex_counts = (
        data["patient_sex"]
        .fillna("[MISSING]")
        .astype(str)
        .replace("", "[MISSING]")
        .value_counts()
    )

    for sex, count in sex_counts.items():

        demographic_rows.append({
            "reactionmeddrapt": reaction_name,
            "dimension": "sex",
            "category": sex,
            "case_count": int(count),
            "percentage_within_candidate": round(
                count / len(data) * 100, 2
            )
        })

    age = pd.to_numeric(
        data["patient_age"],
        errors="coerce"
    )

    age_groups = pd.cut(
        age,
        bins=[-1, 17, 44, 64, 74, 84, 200],
        labels=[
            "0-17",
            "18-44",
            "45-64",
            "65-74",
            "75-84",
            "85+"
        ]
    )

    age_counts = age_groups.value_counts().sort_index()

    for age_group, count in age_counts.items():

        if pd.isna(age_group):
            continue

        demographic_rows.append({
            "reactionmeddrapt": reaction_name,
            "dimension": "age_group",
            "category": str(age_group),
            "case_count": int(count),
            "percentage_within_candidate": round(
                count / len(data) * 100, 2
            )
        })


demographics = pd.DataFrame(demographic_rows)

demographics.to_csv(
    OUT_DEMOGRAPHICS,
    index=False
)

print(f"PASS - Candidate demographic analysis created:")
print(OUT_DEMOGRAPHICS)


# ======================================================================
# COUNTRY PATTERNS
# ======================================================================

section("CANDIDATE REPORTING COUNTRY PATTERNS")

country_rows = []

for reaction_name in sorted(candidate_names):

    case_ids = candidate_reactions[
        candidate_reactions["reactionmeddrapt"]
        .astype(str)
        .str.strip()
        == reaction_name
    ]["safetyreportid"].unique()

    data = integrated[
        integrated["safetyreportid"].isin(case_ids)
    ]

    counts = (
        data["primarysourcecountry"]
        .fillna("[MISSING]")
        .astype(str)
        .replace("", "[MISSING]")
        .value_counts()
    )

    for country, count in counts.items():

        country_rows.append({
            "reactionmeddrapt": reaction_name,
            "country": country,
            "case_count": int(count),
            "percentage_within_candidate": round(
                count / len(data) * 100, 2
            )
        })


countries = pd.DataFrame(country_rows)

countries = countries.sort_values(
    ["reactionmeddrapt", "case_count"],
    ascending=[True, False]
)

countries.to_csv(
    OUT_COUNTRIES,
    index=False
)

print(f"PASS - Candidate country analysis created:")
print(OUT_COUNTRIES)


# ======================================================================
# CO-MEDICATION PATTERN ANALYSIS
# ======================================================================

section("CANDIDATE CO-MEDICATION PATTERNS")

product_rows = []

for reaction_name in sorted(candidate_names):

    case_ids = candidate_reactions[
        candidate_reactions["reactionmeddrapt"]
        .astype(str)
        .str.strip()
        == reaction_name
    ]["safetyreportid"].unique()

    data = integrated[
        integrated["safetyreportid"].isin(case_ids)
    ]

    counter = {}

    for products in data["drug_products"]:

        for product in split_products(products):

            product_upper = product.upper()

            counter[product_upper] = (
                counter.get(product_upper, 0) + 1
            )

    for product, count in counter.items():

        product_rows.append({
            "reactionmeddrapt": reaction_name,
            "product": product,
            "case_count": count,
            "percentage_within_candidate": round(
                count / len(data) * 100, 2
            )
        })


products = pd.DataFrame(product_rows)

products = products.sort_values(
    ["reactionmeddrapt", "case_count"],
    ascending=[True, False]
)

products.to_csv(
    OUT_PRODUCTS,
    index=False
)

print(f"PASS - Candidate product patterns created:")
print(OUT_PRODUCTS)


# ======================================================================
# OVERALL SUMMARY
# ======================================================================

section("PHASE 6 SUMMARY")

summary = pd.DataFrame([{
    "integrated_cases": len(integrated),
    "bisoprolol_cases": len(cohort),
    "candidate_reactions": len(candidate_names),
    "candidate_case_reaction_rows": len(candidate_reactions),
    "candidate_unique_cases": candidate_reactions[
        "safetyreportid"
    ].nunique(),
    "unique_raw_reaction_terms": reactions[
        "reactionmeddrapt"
    ].nunique(),
    "comparator_available": False,
    "ror_available": False,
    "prr_available": False,
    "analysis_type": "descriptive_exploratory",
    "causality_established": False,
    "disproportionality_established": False,
}])

summary.to_csv(
    OUT_SUMMARY,
    index=False
)

print(f"PASS - Phase 6 summary created:")
print(OUT_SUMMARY)


# ======================================================================
# DISPLAY TOP PROFILES
# ======================================================================

section("TOP CANDIDATE PROFILES")

display_columns = [
    "reactionmeddrapt",
    "case_count",
    "percentage_of_all_cases",
    "serious_case_count",
    "serious_percentage",
    "death_case_count",
    "hospitalization_case_count",
    "mean_age",
    "median_age",
]

print(
    profiles[display_columns]
    .to_string(index=False)
)


# ======================================================================
# SAFETY STATEMENT
# ======================================================================

section("ANALYTICAL SAFETY")

print("Comparator cohort available : NO")
print("ROR calculated              : NO")
print("PRR calculated              : NO")
print("Causality established       : NO")
print("Disproportionality claim    : NO")
print()
print(
    "Phase 6 remains descriptive and exploratory."
)
print(
    "Candidate frequencies do not establish causality."
)
print(
    "Co-medication patterns are descriptive and do not prove interaction."
)


# ======================================================================
# COMPLETE
# ======================================================================

section("PHASE 6 ANALYSIS COMPLETE")

print("Generated files:")
print(" - phase6_candidate_profiles.csv")
print(" - phase6_candidate_demographics.csv")
print(" - phase6_candidate_countries.csv")
print(" - phase6_candidate_products.csv")
print(" - phase6_analysis_summary.csv")

print()
print("Phase 6 analysis is COMPLETE.")
print("Proceed to Phase 6 validation before starting Phase 7.")