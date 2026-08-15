import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

DRUG_FILE = os.path.join(DATA_DIR, "normalized_drugs.csv")
REACTION_FILE = os.path.join(DATA_DIR, "normalized_reactions.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "integrated_icsr_cases.csv")


def fail(message):
    print(f"FAIL - {message}")
    raise SystemExit(1)


print("=" * 90)
print("PHASE 4 - ICSR CASE INTEGRATION")
print("=" * 90)

# ------------------------------------------------------------------
# FILE CHECK
# ------------------------------------------------------------------

print("\n" + "=" * 90)
print("FILE CHECK")
print("-" * 90)

if not os.path.exists(DRUG_FILE):
    fail(f"Missing file: {DRUG_FILE}")

if not os.path.exists(REACTION_FILE):
    fail(f"Missing file: {REACTION_FILE}")

print("PASS - normalized_drugs.csv")
print("PASS - normalized_reactions.csv")

# ------------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------------

print("\n" + "=" * 90)
print("LOADING NORMALIZED DATASETS")
print("-" * 90)

drugs = pd.read_csv(DRUG_FILE, dtype=str, keep_default_na=False)
reactions = pd.read_csv(REACTION_FILE, dtype=str, keep_default_na=False)

print(f"Drug rows     : {len(drugs)}")
print(f"Reaction rows : {len(reactions)}")

# ------------------------------------------------------------------
# COLUMN VALIDATION
# ------------------------------------------------------------------

print("\n" + "=" * 90)
print("COLUMN VALIDATION")
print("-" * 90)

required_drug_columns = [
    "safetyreportid",
    "safetyreportversion",
    "drug_index",
    "drug_count",
    "medicinal_product",
]

required_reaction_columns = [
    "safetyreportid",
    "safetyreportversion",
    "reaction_index",
    "reactionmeddrapt",
]

for column in required_drug_columns:
    if column not in drugs.columns:
        fail(f"Missing drug column: {column}")

for column in required_reaction_columns:
    if column not in reactions.columns:
        fail(f"Missing reaction column: {column}")

print("PASS - Required drug columns present")
print("PASS - Required reaction columns present")

# ------------------------------------------------------------------
# CASE SETS
# ------------------------------------------------------------------

print("\n" + "=" * 90)
print("CASE COVERAGE")
print("-" * 90)

drug_cases = set(drugs["safetyreportid"])
reaction_cases = set(reactions["safetyreportid"])

print(f"Drug cases     : {len(drug_cases):,}")
print(f"Reaction cases : {len(reaction_cases):,}")

missing_reaction_cases = drug_cases - reaction_cases
missing_drug_cases = reaction_cases - drug_cases

if missing_reaction_cases:
    print(
        f"WARNING - {len(missing_reaction_cases)} drug cases "
        "have no reaction records."
    )

if missing_drug_cases:
    print(
        f"WARNING - {len(missing_drug_cases)} reaction cases "
        "have no drug records."
    )

common_cases = drug_cases & reaction_cases

print(f"Common cases   : {len(common_cases):,}")

# ------------------------------------------------------------------
# CASE-LEVEL AGGREGATION
# ------------------------------------------------------------------

print("\n" + "=" * 90)
print("BUILDING CASE-LEVEL INTEGRATION")
print("-" * 90)

# One row per case.
# Drugs and reactions remain separate pipe-delimited structures.
# This avoids creating an artificial drug x reaction Cartesian product.

drug_group = (
    drugs.groupby("safetyreportid", sort=False)
    .agg(
        drug_count=("drug_index", "count"),
        drug_products=(
            "medicinal_product",
            lambda x: " | ".join(
                dict.fromkeys(v.strip() for v in x if v.strip())
            ),
        ),
        drug_records=(
            "drug_index",
            lambda x: " | ".join(v.strip() for v in x if v.strip()),
        ),
    )
    .reset_index()
)

reaction_group = (
    reactions.groupby("safetyreportid", sort=False)
    .agg(
        reaction_count=("reaction_index", "count"),
        reaction_terms=(
            "reactionmeddrapt",
            lambda x: " | ".join(
                dict.fromkeys(v.strip() for v in x if v.strip())
            ),
        ),
        reaction_records=(
            "reaction_index",
            lambda x: " | ".join(v.strip() for v in x if v.strip()),
        ),
    )
    .reset_index()
)

# ------------------------------------------------------------------
# CASE METADATA
# ------------------------------------------------------------------

metadata_columns = [
    "safetyreportid",
    "safetyreportversion",
    "receivedate",
    "report_date",
    "transmissiondate",
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
]

metadata_columns = [
    column for column in metadata_columns
    if column in drugs.columns
]

metadata = (
    drugs[metadata_columns]
    .drop_duplicates(subset=["safetyreportid"])
    .copy()
)

# ------------------------------------------------------------------
# MERGE
# ------------------------------------------------------------------

integrated = metadata.merge(
    drug_group,
    on="safetyreportid",
    how="outer",
    validate="one_to_one",
)

integrated = integrated.merge(
    reaction_group,
    on="safetyreportid",
    how="outer",
    validate="one_to_one",
)

# ------------------------------------------------------------------
# CASE FLAGS
# ------------------------------------------------------------------

integrated["has_drug_records"] = (
    integrated["drug_count"].fillna(0).astype(int) > 0
)

integrated["has_reaction_records"] = (
    integrated["reaction_count"].fillna(0).astype(int) > 0
)

integrated["drug_count"] = (
    integrated["drug_count"]
    .fillna(0)
    .astype(int)
)

integrated["reaction_count"] = (
    integrated["reaction_count"]
    .fillna(0)
    .astype(int)
)

integrated["case_integration_status"] = integrated.apply(
    lambda row:
        "COMPLETE"
        if row["has_drug_records"] and row["has_reaction_records"]
        else "DRUG_ONLY"
        if row["has_drug_records"]
        else "REACTION_ONLY",
    axis=1,
)

# ------------------------------------------------------------------
# SORT
# ------------------------------------------------------------------

integrated = integrated.sort_values(
    by=["safetyreportid"]
).reset_index(drop=True)

# ------------------------------------------------------------------
# VALIDATION BEFORE WRITE
# ------------------------------------------------------------------

print("\n" + "=" * 90)
print("INTEGRATION QUALITY CHECK")
print("-" * 90)

if integrated["safetyreportid"].duplicated().any():
    fail("Duplicate case IDs detected in integrated dataset.")

if integrated["safetyreportid"].isna().any():
    fail("Missing safety report IDs detected.")

if len(integrated) != len(
    set(drug_cases | reaction_cases)
):
    fail("Integrated case count does not match source case union.")

print("PASS - One row per safety report")
print("PASS - No duplicate case IDs")
print("PASS - No missing safety report IDs")
print("PASS - Case coverage matches source datasets")

# ------------------------------------------------------------------
# SAVE
# ------------------------------------------------------------------

integrated.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig",
)

# ------------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------------

print("\n" + "=" * 90)
print("PHASE 4 INTEGRATION SUMMARY")
print("-" * 90)

print(f"Integrated cases : {len(integrated):,}")
print(f"Drug cases       : {len(drug_cases):,}")
print(f"Reaction cases   : {len(reaction_cases):,}")
print(f"Common cases     : {len(common_cases):,}")

print("\nCASE STATUS")
print("-" * 90)

print(
    integrated["case_integration_status"]
    .value_counts()
    .to_string()
)

print("\nDRUG STATISTICS")
print("-" * 90)

print(f"Total drug records       : {len(drugs):,}")
print(
    f"Maximum drugs per case  : "
    f"{drugs.groupby('safetyreportid').size().max():,}"
)

print("\nREACTION STATISTICS")
print("-" * 90)

print(f"Total reaction records  : {len(reactions):,}")
print(
    f"Maximum reactions/case  : "
    f"{reactions.groupby('safetyreportid').size().max():,}"
)

print("\nOUTPUT")
print("-" * 90)
print(f"Integrated dataset : {OUTPUT_FILE}")

print("\n" + "=" * 90)
print("PHASE 4 CASE INTEGRATION COMPLETE")
print("=" * 90)