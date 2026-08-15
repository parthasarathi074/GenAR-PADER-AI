import os
import sys
import pandas as pd
from collections import Counter

# =============================================================================
# PHASE 6 - SIGNAL ANALYSIS & CLINICAL PATTERN INVESTIGATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_FILE = os.path.join(
    DATA_DIR,
    "integrated_icsr_cases.csv"
)

PHASE5_CASE_FILE = os.path.join(
    DATA_DIR,
    "phase5_case_cohort.csv"
)

PHASE5_REACTION_FILE = os.path.join(
    DATA_DIR,
    "phase5_case_reactions.csv"
)

PHASE5_CANDIDATE_FILE = os.path.join(
    DATA_DIR,
    "phase5_signal_candidates.csv"
)

SEPARATOR = "=" * 100
SUB_SEPARATOR = "-" * 100


def section(title):
    print()
    print(SEPARATOR)
    print(title)
    print(SEPARATOR)


def subsection(title):
    print()
    print(SUB_SEPARATOR)
    print(title)
    print(SUB_SEPARATOR)


def fail(message):
    print(f"FAIL - {message}")
    sys.exit(1)


# =============================================================================
# FILE CHECK
# =============================================================================

section("PHASE 6 - SIGNAL ANALYSIS & CLINICAL PATTERN INVESTIGATION")

section("FILE CHECK")

required_files = {
    "integrated_icsr_cases.csv": INPUT_FILE,
    "phase5_case_cohort.csv": PHASE5_CASE_FILE,
    "phase5_case_reactions.csv": PHASE5_REACTION_FILE,
    "phase5_signal_candidates.csv": PHASE5_CANDIDATE_FILE,
}

for name, path in required_files.items():
    if os.path.exists(path):
        print(f"PASS - {name}")
    else:
        fail(f"{name} not found at {path}")


# =============================================================================
# LOAD DATASETS
# =============================================================================

section("LOADING PHASE 6 DATASETS")

try:
    integrated = pd.read_csv(INPUT_FILE, dtype=str)
    cohort = pd.read_csv(PHASE5_CASE_FILE, dtype=str)
    reactions = pd.read_csv(PHASE5_REACTION_FILE, dtype=str)
    candidates = pd.read_csv(PHASE5_CANDIDATE_FILE, dtype=str)
except Exception as exc:
    fail(f"Unable to load dataset: {exc}")


print(f"Integrated rows       : {len(integrated):,}")
print(f"Case cohort rows      : {len(cohort):,}")
print(f"Case × reaction rows  : {len(reactions):,}")
print(f"Signal candidates     : {len(candidates):,}")


# =============================================================================
# COLUMN INVENTORY
# =============================================================================

section("INTEGRATED DATASET COLUMN INVENTORY")

for i, column in enumerate(integrated.columns, start=1):
    print(f"{i:02d}. {column}")


section("PHASE 5 REACTION DATASET COLUMN INVENTORY")

for i, column in enumerate(reactions.columns, start=1):
    print(f"{i:02d}. {column}")


section("PHASE 5 CANDIDATE DATASET COLUMN INVENTORY")

for i, column in enumerate(candidates.columns, start=1):
    print(f"{i:02d}. {column}")


# =============================================================================
# REQUIRED COLUMN VALIDATION
# =============================================================================

section("REQUIRED COLUMN VALIDATION")

required_integrated = [
    "safetyreportid",
    "safetyreportversion",
    "primarysourcecountry",
    "occurcountry",
    "reporttype",
    "serious",
    "seriousnessdeath",
    "seriousnesslifethreatening",
    "seriousnesshospitalization",
    "seriousnessdisabling",
    "patient_sex",
    "patient_age",
    "patient_age_unit",
    "drug_count",
    "reaction_count",
    "drug_products",
    "reaction_terms",
    "case_integration_status",
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

for column in required_integrated:
    if column in integrated.columns:
        print(f"PASS - Integrated column: {column}")
    else:
        fail(f"Missing integrated column: {column}")

for column in required_reactions:
    if column in reactions.columns:
        print(f"PASS - Reaction column: {column}")
    else:
        fail(f"Missing reaction column: {column}")

for column in required_candidates:
    if column in candidates.columns:
        print(f"PASS - Candidate column: {column}")
    else:
        fail(f"Missing candidate column: {column}")


# =============================================================================
# CASE-LEVEL VALIDATION
# =============================================================================

section("CASE-LEVEL STRUCTURE VALIDATION")

integrated_case_ids = integrated["safetyreportid"].dropna().astype(str)

print(f"Integrated cases       : {integrated_case_ids.nunique():,}")
print(f"Integrated rows        : {len(integrated):,}")

duplicate_cases = integrated_case_ids[
    integrated_case_ids.duplicated(keep=False)
]

if len(duplicate_cases) == 0:
    print("PASS - Integrated dataset contains one row per case.")
else:
    print(
        f"WARNING - {duplicate_cases.nunique():,} case IDs "
        f"appear more than once."
    )


# =============================================================================
# CASE COVERAGE
# =============================================================================

section("CASE COVERAGE")

integrated_cases = set(integrated_case_ids)

cohort_cases = set(
    cohort["safetyreportid"]
    .dropna()
    .astype(str)
)

reaction_cases = set(
    reactions["safetyreportid"]
    .dropna()
    .astype(str)
)

print(f"Integrated cases : {len(integrated_cases):,}")
print(f"Cohort cases     : {len(cohort_cases):,}")
print(f"Reaction cases   : {len(reaction_cases):,}")

missing_from_cohort = integrated_cases - cohort_cases
missing_from_reactions = integrated_cases - reaction_cases

print()

if not missing_from_cohort:
    print("PASS - All integrated cases are represented in the Phase 5 cohort.")
else:
    print(
        f"WARNING - {len(missing_from_cohort):,} integrated cases "
        f"are missing from cohort."
    )

if not missing_from_reactions:
    print("PASS - All integrated cases are represented in reaction data.")
else:
    print(
        f"WARNING - {len(missing_from_reactions):,} integrated cases "
        f"are missing from reaction data."
    )


# =============================================================================
# BISOPROLOL COHORT
# =============================================================================

section("BISOPROLOL EXPOSURE STRUCTURE")

if "bisoprolol_exposed" in cohort.columns:
    exposure_counts = cohort["bisoprolol_exposed"].value_counts(
        dropna=False
    )

    for value, count in exposure_counts.items():
        print(f"{str(value):20s} {count:>6,}")
else:
    print("WARNING - bisoprolol_exposed column unavailable.")


# =============================================================================
# COMPARATOR CHECK
# =============================================================================

section("COMPARATOR COHORT INVESTIGATION")

if "bisoprolol_exposed" in cohort.columns:

    exposure_values = (
        cohort["bisoprolol_exposed"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    non_exposed = (exposure_values == "false").sum()
    non_exposed_alt = (exposure_values == "no").sum()
    non_exposed_zero = (exposure_values == "0").sum()

    comparator_count = max(
        non_exposed,
        non_exposed_alt,
        non_exposed_zero
    )

    if comparator_count == 0:
        print("INFO - No internal non-Bisoprolol comparator detected.")
        print("INFO - ROR/PRR remains unavailable.")
        print("INFO - Phase 6 will remain descriptive/exploratory.")
    else:
        print(
            f"INFO - Potential comparator records detected: "
            f"{comparator_count:,}"
        )
else:
    print("WARNING - Comparator status cannot be determined.")


# =============================================================================
# CANDIDATE REACTION INVESTIGATION
# =============================================================================

section("SIGNAL CANDIDATE INVESTIGATION")

candidate_terms = (
    candidates["reactionmeddrapt"]
    .dropna()
    .astype(str)
    .str.strip()
)

candidate_terms = [
    term for term in candidate_terms
    if term
]

print(f"Candidate reactions : {len(candidate_terms):,}")

for index, term in enumerate(candidate_terms, start=1):
    print(f"{index:02d}. {term}")


# =============================================================================
# CASE × REACTION DEDUPLICATION INVESTIGATION
# =============================================================================

section("CASE × REACTION CARDINALITY INVESTIGATION")

reaction_data = reactions.copy()

reaction_data["safetyreportid"] = (
    reaction_data["safetyreportid"]
    .fillna("")
    .astype(str)
    .str.strip()
)

reaction_data["reactionmeddrapt"] = (
    reaction_data["reactionmeddrapt"]
    .fillna("")
    .astype(str)
    .str.strip()
)

unique_case_reaction = reaction_data[
    ["safetyreportid", "reactionmeddrapt"]
].drop_duplicates()

print(
    f"Raw case × reaction rows       : "
    f"{len(reaction_data):,}"
)

print(
    f"Unique case × reaction pairs   : "
    f"{len(unique_case_reaction):,}"
)

print(
    f"Unique cases                    : "
    f"{unique_case_reaction['safetyreportid'].nunique():,}"
)

print(
    f"Unique reaction terms           : "
    f"{unique_case_reaction['reactionmeddrapt'].nunique():,}"
)

duplicates_removed = (
    len(reaction_data) -
    len(unique_case_reaction)
)

print(
    f"Duplicate case × reaction rows : "
    f"{duplicates_removed:,}"
)


# =============================================================================
# CANDIDATE CASE-LEVEL COUNTS
# =============================================================================

section("CANDIDATE CASE-LEVEL FREQUENCY VERIFICATION")

candidate_frequency = []

for term in candidate_terms:

    matches = unique_case_reaction[
        unique_case_reaction["reactionmeddrapt"].str.casefold()
        == term.casefold()
    ]

    case_count = matches["safetyreportid"].nunique()

    candidate_frequency.append(
        {
            "reaction": term,
            "unique_case_count": case_count,
        }
    )

candidate_frequency_df = pd.DataFrame(candidate_frequency)

if not candidate_frequency_df.empty:
    candidate_frequency_df = candidate_frequency_df.sort_values(
        by="unique_case_count",
        ascending=False
    )

    for _, row in candidate_frequency_df.iterrows():
        print(
            f"{int(row['unique_case_count']):>5}  "
            f"{row['reaction']}"
        )


# =============================================================================
# SERIOUSNESS STRUCTURE
# =============================================================================

section("SERIOUSNESS STRUCTURE")

seriousness_columns = [
    "serious",
    "seriousnessdeath",
    "seriousnesslifethreatening",
    "seriousnesshospitalization",
    "seriousnessdisabling",
]

for column in seriousness_columns:

    print()
    print(column)
    print(SUB_SEPARATOR)

    if column not in integrated.columns:
        print("WARNING - Column unavailable.")
        continue

    counts = integrated[column].fillna("[MISSING]").value_counts()

    for value, count in counts.items():
        percentage = count / len(integrated) * 100

        print(
            f"{str(value):35s}"
            f"{count:>6,} "
            f"({percentage:6.2f}%)"
        )


# =============================================================================
# CANDIDATE-SPECIFIC SERIOUSNESS INVESTIGATION
# =============================================================================

section("CANDIDATE-SPECIFIC SERIOUSNESS INVESTIGATION")

integrated_indexed = integrated.set_index(
    integrated["safetyreportid"].astype(str)
)

for term in candidate_terms:

    matching_cases = unique_case_reaction[
        unique_case_reaction["reactionmeddrapt"].str.casefold()
        == term.casefold()
    ]["safetyreportid"].unique()

    matching_cases = [str(case_id) for case_id in matching_cases]

    subset = integrated[
        integrated["safetyreportid"]
        .astype(str)
        .isin(matching_cases)
    ]

    serious_count = 0

    if "serious" in subset.columns:
        serious_values = (
            subset["serious"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.strip()
        )

        serious_count = (serious_values == "serious").sum()

    percentage = (
        serious_count / len(subset) * 100
        if len(subset) > 0
        else 0
    )

    print(
        f"{term:40s} "
        f"cases={len(subset):>4} "
        f"serious={serious_count:>4} "
        f"serious%={percentage:6.2f}%"
    )


# =============================================================================
# DEMOGRAPHIC STRUCTURE
# =============================================================================

section("DEMOGRAPHIC STRUCTURE")

print("SEX")
print(SUB_SEPARATOR)

if "patient_sex" in integrated.columns:

    sex_counts = (
        integrated["patient_sex"]
        .fillna("[MISSING]")
        .value_counts()
    )

    for value, count in sex_counts.items():
        percentage = count / len(integrated) * 100

        print(
            f"{str(value):20s}"
            f"{count:>6,} "
            f"({percentage:6.2f}%)"
        )


print()
print("AGE UNIT")
print(SUB_SEPARATOR)

if "patient_age_unit" in integrated.columns:

    age_unit_counts = (
        integrated["patient_age_unit"]
        .fillna("[MISSING]")
        .value_counts()
    )

    for value, count in age_unit_counts.items():
        percentage = count / len(integrated) * 100

        print(
            f"{str(value):20s}"
            f"{count:>6,} "
            f"({percentage:6.2f}%)"
        )


# =============================================================================
# AGE QUALITY CHECK
# =============================================================================

section("AGE QUALITY INVESTIGATION")

age_numeric = pd.to_numeric(
    integrated["patient_age"],
    errors="coerce"
)

valid_age = age_numeric.dropna()

print(f"Valid age records : {len(valid_age):,}")
print(f"Missing age       : {age_numeric.isna().sum():,}")

if len(valid_age) > 0:

    print(f"Minimum age       : {valid_age.min():.1f}")
    print(f"Maximum age       : {valid_age.max():.1f}")
    print(f"Mean age          : {valid_age.mean():.1f}")
    print(f"Median age        : {valid_age.median():.1f}")


# =============================================================================
# COUNTRY STRUCTURE
# =============================================================================

section("REPORTING COUNTRY STRUCTURE")

if "primarysourcecountry" in integrated.columns:

    country_counts = (
        integrated["primarysourcecountry"]
        .fillna("[MISSING]")
        .value_counts()
    )

    print(
        f"Unique reporting countries : "
        f"{country_counts.shape[0]:,}"
    )

    print()
    print("TOP 20 COUNTRIES")
    print(SUB_SEPARATOR)

    for country, count in country_counts.head(20).items():

        percentage = count / len(integrated) * 100

        print(
            f"{str(country):25s}"
            f"{count:>6,} "
            f"({percentage:6.2f}%)"
        )


# =============================================================================
# REPORT TYPE
# =============================================================================

section("REPORT TYPE STRUCTURE")

if "reporttype" in integrated.columns:

    report_counts = (
        integrated["reporttype"]
        .fillna("[MISSING]")
        .value_counts()
    )

    for value, count in report_counts.items():

        percentage = count / len(integrated) * 100

        print(
            f"{str(value):35s}"
            f"{count:>6,} "
            f"({percentage:6.2f}%)"
        )


# =============================================================================
# REACTION OUTCOME AVAILABILITY
# =============================================================================

section("REACTION OUTCOME STRUCTURE")

if "reactionoutcome" in reactions.columns:

    outcome_counts = (
        reactions["reactionoutcome"]
        .fillna("[MISSING]")
        .astype(str)
        .str.strip()
        .value_counts()
    )

    print(
        f"Unique outcome values : "
        f"{len(outcome_counts):,}"
    )

    for outcome, count in outcome_counts.items():

        percentage = count / len(reactions) * 100

        print(
            f"{str(outcome):40s}"
            f"{count:>6,} "
            f"({percentage:6.2f}%)"
        )

else:
    print(
        "INFO - reactionoutcome is not present in "
        "phase5_case_reactions.csv."
    )


# =============================================================================
# CANDIDATE OUTCOME INVESTIGATION
# =============================================================================

section("CANDIDATE REACTION OUTCOME INVESTIGATION")

if "reactionoutcome" in reactions.columns:

    for term in candidate_terms:

        subset = reactions[
            reactions["reactionmeddrapt"]
            .fillna("")
            .astype(str)
            .str.casefold()
            == term.casefold()
        ]

        print()
        print(term)
        print(SUB_SEPARATOR)

        outcomes = (
            subset["reactionoutcome"]
            .fillna("[MISSING]")
            .astype(str)
            .str.strip()
            .value_counts()
        )

        if outcomes.empty:
            print("No outcome records found.")
        else:
            for outcome, count in outcomes.items():
                print(
                    f"{str(outcome):40s}"
                    f"{count:>6,}"
                )


# =============================================================================
# DRUG PRODUCT PATTERN INVESTIGATION
# =============================================================================

section("DRUG PRODUCT PATTERN INVESTIGATION")

if "drug_products" in integrated.columns:

    drug_counter = Counter()

    for value in integrated["drug_products"].fillna(""):

        products = [
            product.strip()
            for product in str(value).split("|")
            if product.strip()
        ]

        for product in products:
            drug_counter[product.upper()] += 1

    print(
        f"Unique product strings : "
        f"{len(drug_counter):,}"
    )

    print()
    print("TOP 30 PRODUCT STRINGS")
    print(SUB_SEPARATOR)

    for product, count in drug_counter.most_common(30):

        print(
            f"{count:>6,}  {product}"
        )


# =============================================================================
# CASE SIZE STRUCTURE
# =============================================================================

section("CASE SIZE STRUCTURE")

for column, label in [
    ("drug_count", "DRUGS PER CASE"),
    ("reaction_count", "REACTIONS PER CASE"),
]:

    print()
    print(label)
    print(SUB_SEPARATOR)

    numeric_values = pd.to_numeric(
        integrated[column],
        errors="coerce"
    ).dropna()

    if len(numeric_values) == 0:
        print("No numeric records available.")
        continue

    print(f"Minimum : {numeric_values.min():.0f}")
    print(f"Maximum : {numeric_values.max():.0f}")
    print(f"Mean    : {numeric_values.mean():.2f}")
    print(f"Median  : {numeric_values.median():.2f}")


# =============================================================================
# PHASE 6 ANALYTICAL READINESS
# =============================================================================

section("PHASE 6 ANALYTICAL READINESS")

checks = []

checks.append(
    (
        "Integrated case-level dataset available",
        len(integrated) > 0
    )
)

checks.append(
    (
        "Phase 5 case cohort available",
        len(cohort) > 0
    )
)

checks.append(
    (
        "Phase 5 case × reaction dataset available",
        len(reactions) > 0
    )
)

checks.append(
    (
        "Phase 5 signal candidates available",
        len(candidates) > 0
    )
)

checks.append(
    (
        "Candidate case-level frequencies verified",
        not candidate_frequency_df.empty
    )
)

for description, passed in checks:
    print(
        f"{'PASS' if passed else 'FAIL'} - {description}"
    )


# =============================================================================
# FINAL SUMMARY
# =============================================================================

section("PHASE 6 INVESTIGATION SUMMARY")

print(
    f"Integrated cases                 : "
    f"{integrated['safetyreportid'].nunique():,}"
)

print(
    f"Phase 5 candidate reactions      : "
    f"{len(candidate_terms):,}"
)

print(
    f"Unique raw case × reaction rows  : "
    f"{len(reaction_data):,}"
)

print(
    f"Unique case × reaction pairs     : "
    f"{len(unique_case_reaction):,}"
)

print(
    f"Unique reaction terms             : "
    f"{unique_case_reaction['reactionmeddrapt'].nunique():,}"
)

print(
    f"Duplicate case × reaction rows   : "
    f"{duplicates_removed:,}"
)

print()
print("COMPARATOR STATUS")
print(SUB_SEPARATOR)

print(
    "No internal non-Bisoprolol comparator "
    "should be assumed unless explicitly detected."
)

print(
    "ROR/PRR must NOT be calculated from this "
    "single-exposure cohort."
)

print()
print("ANALYTICAL STATUS")
print(SUB_SEPARATOR)

print(
    "Phase 6 investigation is descriptive and exploratory."
)

print(
    "No causal relationship is established."
)

print(
    "No disproportionality conclusion is established."
)

print()
print(SEPARATOR)
print("PHASE 6 INVESTIGATION COMPLETE")
print(SEPARATOR)