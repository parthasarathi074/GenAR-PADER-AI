import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_FILE = os.path.join(
    DATA_DIR,
    "integrated_icsr_cases.csv"
)


def fail(message):
    print(f"FAIL - {message}")
    raise SystemExit(1)


print("=" * 100)
print("PHASE 5 - PHARMACOVIGILANCE DATA INVESTIGATION")
print("=" * 100)

# ==================================================================
# FILE CHECK
# ==================================================================

print("\n" + "=" * 100)
print("FILE CHECK")
print("-" * 100)

if not os.path.exists(INPUT_FILE):
    fail(
        "integrated_icsr_cases.csv not found. "
        "Complete Phase 4 first."
    )

print("PASS - integrated_icsr_cases.csv")

# ==================================================================
# LOAD DATA
# ==================================================================

print("\n" + "=" * 100)
print("LOADING INTEGRATED DATASET")
print("-" * 100)

df = pd.read_csv(
    INPUT_FILE,
    dtype=str,
    keep_default_na=False
)

print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns):,}")

# ==================================================================
# COLUMN INVENTORY
# ==================================================================

print("\n" + "=" * 100)
print("COLUMN INVENTORY")
print("-" * 100)

for index, column in enumerate(df.columns, start=1):
    print(f"{index:02d}. {column}")

# ==================================================================
# REQUIRED COLUMN CHECK
# ==================================================================

print("\n" + "=" * 100)
print("REQUIRED ANALYTICAL COLUMNS")
print("-" * 100)

required_columns = [
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

for column in required_columns:
    if column not in df.columns:
        fail(f"Missing required analytical column: {column}")

    print(f"PASS - {column}")

# ==================================================================
# BASIC CASE STATISTICS
# ==================================================================

print("\n" + "=" * 100)
print("CASE STATISTICS")
print("-" * 100)

print(f"Unique cases              : {df['safetyreportid'].nunique():,}")
print(
    f"Complete integrated cases : "
    f"{(df['case_integration_status'] == 'COMPLETE').sum():,}"
)

print(
    f"Cases with drug records   : "
    f"{(pd.to_numeric(df['drug_count']) > 0).sum():,}"
)

print(
    f"Cases with reactions      : "
    f"{(pd.to_numeric(df['reaction_count']) > 0).sum():,}"
)

# ==================================================================
# BISOPROLOL EXPOSURE INVESTIGATION
# ==================================================================

print("\n" + "=" * 100)
print("BISOPROLOL EXPOSURE INVESTIGATION")
print("-" * 100)

drug_text = (
    df["drug_products"]
    .fillna("")
    .astype(str)
    .str.upper()
)

bisoprolol_mask = drug_text.str.contains(
    "BISOPROLOL",
    regex=False
)

bisoprolol_cases = df[bisoprolol_mask].copy()

print(f"Cases containing BISOPROLOL : {len(bisoprolol_cases):,}")

if len(bisoprolol_cases) == 0:
    print("WARNING - No Bisoprolol cases detected.")
else:
    print("PASS - Bisoprolol exposure records detected.")

# ==================================================================
# BISOPROLOL PRODUCT DETAILS
# ==================================================================

print("\n" + "=" * 100)
print("BISOPROLOL PRODUCT OCCURRENCES")
print("-" * 100)

products = {}

for value in bisoprolol_cases["drug_products"]:
    for product in str(value).split("|"):
        product = product.strip()

        if "BISOPROLOL" in product.upper():
            products[product] = products.get(product, 0) + 1

if products:
    for product, count in sorted(
        products.items(),
        key=lambda item: (-item[1], item[0])
    ):
        print(f"{count:5d}  {product}")
else:
    print("No Bisoprolol product names identified.")

# ==================================================================
# REACTION FREQUENCY
# ==================================================================

print("\n" + "=" * 100)
print("REACTION FREQUENCY")
print("-" * 100)

reaction_counter = {}

for value in bisoprolol_cases["reaction_terms"]:
    for reaction in str(value).split("|"):

        reaction = reaction.strip()

        if not reaction:
            continue

        reaction_counter[reaction] = (
            reaction_counter.get(reaction, 0) + 1
        )

print(
    f"Unique reported reaction terms : "
    f"{len(reaction_counter):,}"
)

print("\nTOP 30 REPORTED REACTIONS")
print("-" * 100)

for reaction, count in sorted(
    reaction_counter.items(),
    key=lambda item: (-item[1], item[0])
)[:30]:

    percentage = (
        count / len(bisoprolol_cases) * 100
        if len(bisoprolol_cases) > 0
        else 0
    )

    print(
        f"{count:5d}  "
        f"{percentage:6.2f}%  "
        f"{reaction}"
    )

# ==================================================================
# SERIOUSNESS
# ==================================================================

print("\n" + "=" * 100)
print("SERIOUSNESS ANALYSIS")
print("-" * 100)

serious_columns = [
    "serious",
    "seriousnessdeath",
    "seriousnesslifethreatening",
    "seriousnesshospitalization",
    "seriousnessdisabling",
]

for column in serious_columns:

    print(f"\n{column}")
    print("-" * 70)

    counts = (
        bisoprolol_cases[column]
        .replace("", "[MISSING]")
        .value_counts()
    )

    for value, count in counts.items():

        percentage = (
            count / len(bisoprolol_cases) * 100
            if len(bisoprolol_cases) > 0
            else 0
        )

        print(
            f"{str(value):35s}"
            f"{count:6d} "
            f"({percentage:6.2f}%)"
        )

# ==================================================================
# DEMOGRAPHIC ANALYSIS
# ==================================================================

print("\n" + "=" * 100)
print("DEMOGRAPHIC ANALYSIS")
print("-" * 100)

print("\nSEX")
print("-" * 70)

sex_counts = (
    bisoprolol_cases["patient_sex"]
    .replace("", "[MISSING]")
    .value_counts()
)

for value, count in sex_counts.items():

    percentage = (
        count / len(bisoprolol_cases) * 100
        if len(bisoprolol_cases) > 0
        else 0
    )

    print(
        f"{str(value):20s}"
        f"{count:6d} "
        f"({percentage:6.2f}%)"
    )

print("\nAGE UNIT")
print("-" * 70)

age_unit_counts = (
    bisoprolol_cases["patient_age_unit"]
    .replace("", "[MISSING]")
    .value_counts()
)

for value, count in age_unit_counts.items():
    print(f"{str(value):20s}{count:6d}")

# ==================================================================
# AGE ANALYSIS
# ==================================================================

print("\n" + "=" * 100)
print("AGE ANALYSIS")
print("-" * 100)

age = pd.to_numeric(
    bisoprolol_cases["patient_age"],
    errors="coerce"
)

valid_age = age.dropna()

if len(valid_age) > 0:

    print(f"Valid age records : {len(valid_age):,}")
    print(f"Missing age       : {age.isna().sum():,}")
    print(f"Minimum age       : {valid_age.min():.1f}")
    print(f"Maximum age       : {valid_age.max():.1f}")
    print(f"Mean age          : {valid_age.mean():.1f}")
    print(f"Median age        : {valid_age.median():.1f}")

    print("\nAGE GROUPS")

    age_groups = pd.cut(
        valid_age,
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

    for group, count in age_counts.items():

        percentage = (
            count / len(valid_age) * 100
        )

        print(
            f"{str(group):10s}"
            f"{count:6d} "
            f"({percentage:6.2f}%)"
        )

else:

    print("No valid age values available.")

# ==================================================================
# COUNTRY ANALYSIS
# ==================================================================

print("\n" + "=" * 100)
print("REPORTING COUNTRY ANALYSIS")
print("-" * 100)

country_counts = (
    bisoprolol_cases["primarysourcecountry"]
    .replace("", "[MISSING]")
    .value_counts()
)

print(
    f"Unique reporting countries : "
    f"{len(country_counts):,}"
)

print("\nTOP 20 COUNTRIES")

for country, count in country_counts.head(20).items():

    percentage = (
        count / len(bisoprolol_cases) * 100
        if len(bisoprolol_cases) > 0
        else 0
    )

    print(
        f"{count:5d} "
        f"({percentage:6.2f}%) "
        f"{country}"
    )

# ==================================================================
# REPORT TYPE
# ==================================================================

print("\n" + "=" * 100)
print("REPORT TYPE")
print("-" * 100)

report_type_counts = (
    bisoprolol_cases["reporttype"]
    .replace("", "[MISSING]")
    .value_counts()
)

for value, count in report_type_counts.items():

    percentage = (
        count / len(bisoprolol_cases) * 100
        if len(bisoprolol_cases) > 0
        else 0
    )

    print(
        f"{str(value):35s}"
        f"{count:6d} "
        f"({percentage:6.2f}%)"
    )

# ==================================================================
# DRUG/REACTION COUNT DISTRIBUTION
# ==================================================================

print("\n" + "=" * 100)
print("DRUG / REACTION COUNT DISTRIBUTION")
print("-" * 100)

drug_counts = pd.to_numeric(
    bisoprolol_cases["drug_count"],
    errors="coerce"
)

reaction_counts = pd.to_numeric(
    bisoprolol_cases["reaction_count"],
    errors="coerce"
)

print("\nDRUGS PER CASE")
print("-" * 70)

print(f"Minimum : {drug_counts.min():.0f}")
print(f"Maximum : {drug_counts.max():.0f}")
print(f"Mean    : {drug_counts.mean():.2f}")
print(f"Median  : {drug_counts.median():.2f}")

print("\nREACTIONS PER CASE")
print("-" * 70)

print(f"Minimum : {reaction_counts.min():.0f}")
print(f"Maximum : {reaction_counts.max():.0f}")
print(f"Mean    : {reaction_counts.mean():.2f}")
print(f"Median  : {reaction_counts.median():.2f}")

# ==================================================================
# SERIOUS CASE REACTION PROFILE
# ==================================================================

print("\n" + "=" * 100)
print("REACTIONS IN SERIOUS BISOPROLOL CASES")
print("-" * 100)

serious_mask = (
    bisoprolol_cases["serious"]
    .astype(str)
    .str.lower()
    .eq("serious")
)

serious_cases = bisoprolol_cases[serious_mask]

print(f"Serious Bisoprolol cases : {len(serious_cases):,}")

serious_reactions = {}

for value in serious_cases["reaction_terms"]:

    for reaction in str(value).split("|"):

        reaction = reaction.strip()

        if not reaction:
            continue

        serious_reactions[reaction] = (
            serious_reactions.get(reaction, 0) + 1
        )

print("\nTOP 20 REACTIONS IN SERIOUS CASES")
print("-" * 100)

for reaction, count in sorted(
    serious_reactions.items(),
    key=lambda item: (-item[1], item[0])
)[:20]:

    print(f"{count:5d}  {reaction}")

# ==================================================================
# HIGH-LEVEL SIGNAL CANDIDATE SCREEN
# ==================================================================

print("\n" + "=" * 100)
print("INITIAL SIGNAL-CANDIDATE SCREEN")
print("-" * 100)

print(
    "This is an exploratory frequency screen only."
)

print(
    "It does NOT establish causality or disproportionality."
)

print(
    "Potential candidates are reactions reported repeatedly "
    "in Bisoprolol-containing cases."
)

candidate_threshold = 5

candidates = [
    (reaction, count)
    for reaction, count in reaction_counter.items()
    if count >= candidate_threshold
]

candidates.sort(
    key=lambda item: (-item[1], item[0])
)

print(
    f"\nCandidates with >= {candidate_threshold} "
    f"Bisoprolol-containing cases: {len(candidates):,}"
)

for reaction, count in candidates[:30]:
    print(f"{count:5d}  {reaction}")

# ==================================================================
# FINAL INVESTIGATION SUMMARY
# ==================================================================

print("\n" + "=" * 100)
print("PHASE 5 INVESTIGATION SUMMARY")
print("-" * 100)

print(f"Total integrated cases       : {len(df):,}")
print(f"Bisoprolol-containing cases  : {len(bisoprolol_cases):,}")
print(f"Unique reaction terms        : {len(reaction_counter):,}")
print(f"Serious Bisoprolol cases     : {len(serious_cases):,}")
print(f"Initial signal candidates    : {len(candidates):,}")

print("\n" + "=" * 100)
print("PHASE 5 INVESTIGATION COMPLETE")
print("=" * 100)

print(
    "\nNo analytical conclusions have been finalized yet."
)

print(
    "The output above is the structural and descriptive "
    "basis for the next Phase 5 analysis step."
)