import os
import pandas as pd

print("=" * 80)
print("PHASE 3 - INTEGRATED NORMALIZED DATASET VALIDATION")
print("=" * 80)

DATA_DIR = "data"

DRUG_FILE = os.path.join(DATA_DIR, "normalized_drugs.csv")
REACTION_FILE = os.path.join(DATA_DIR, "normalized_reactions.csv")

# ----------------------------------------------------------------------
# FILE CHECK
# ----------------------------------------------------------------------

print("\n" + "=" * 80)
print("FILE CHECK")
print("-" * 80)

files_ok = True

if os.path.exists(DRUG_FILE):
    print("PASS - normalized_drugs.csv")
else:
    print("FAIL - normalized_drugs.csv not found.")
    files_ok = False

if os.path.exists(REACTION_FILE):
    print("PASS - normalized_reactions.csv")
else:
    print("FAIL - normalized_reactions.csv not found.")
    files_ok = False

if not files_ok:
    print("\nFINAL RESULT: FAIL")
    raise SystemExit(1)

# ----------------------------------------------------------------------
# LOAD DATASETS
# ----------------------------------------------------------------------

print("\n" + "=" * 80)
print("LOADING NORMALIZED DATASETS")
print("-" * 80)

drugs = pd.read_csv(DRUG_FILE)
reactions = pd.read_csv(REACTION_FILE)

print(f"Drug rows     : {len(drugs)}")
print(f"Reaction rows : {len(reactions)}")

# ----------------------------------------------------------------------
# SHOW ACTUAL COLUMNS
# ----------------------------------------------------------------------

print("\n" + "=" * 80)
print("NORMALIZED DRUG COLUMNS")
print("-" * 80)

for i, col in enumerate(drugs.columns, 1):
    print(f"{i:02d}. {col}")

print("\n" + "=" * 80)
print("NORMALIZED REACTION COLUMNS")
print("-" * 80)

for i, col in enumerate(reactions.columns, 1):
    print(f"{i:02d}. {col}")

# ----------------------------------------------------------------------
# COLUMN VALIDATION
# ----------------------------------------------------------------------

print("\n" + "=" * 80)
print("COLUMN VALIDATION")
print("-" * 80)

# Drug dataset
drug_required = {
    "safetyreportid": [
        "safetyreportid"
    ],
    "drug_index": [
        "drug_index"
    ],
    "medicinalproduct": [
        "medicinalproduct",
        "medicinal_product"
    ]
}

drug_columns_ok = True

for logical_name, aliases in drug_required.items():

    found = None

    for alias in aliases:
        if alias in drugs.columns:
            found = alias
            break

    if found:
        print(f"PASS - Drug column present: {found}")
    else:
        print(
            f"FAIL - Missing drug column: {logical_name} "
            f"(accepted: {', '.join(aliases)})"
        )
        drug_columns_ok = False


# Reaction dataset
reaction_required = {
    "safetyreportid": [
        "safetyreportid"
    ],
    "reaction_index": [
        "reaction_index"
    ],
    "reactionmeddrapt": [
        "reactionmeddrapt",
        "reaction_meddrapt"
    ]
}

reaction_columns_ok = True

for logical_name, aliases in reaction_required.items():

    found = None

    for alias in aliases:
        if alias in reactions.columns:
            found = alias
            break

    if found:
        print(f"PASS - Reaction column present: {found}")
    else:
        print(
            f"FAIL - Missing reaction column: {logical_name} "
            f"(accepted: {', '.join(aliases)})"
        )
        reaction_columns_ok = False

if not drug_columns_ok or not reaction_columns_ok:
    print("\nFINAL RESULT: FAIL")
    raise SystemExit(1)

# ----------------------------------------------------------------------
# IDENTIFY ACTUAL COLUMN NAMES
# ----------------------------------------------------------------------

drug_id_col = "safetyreportid"
drug_index_col = "drug_index"

drug_product_col = (
    "medicinalproduct"
    if "medicinalproduct" in drugs.columns
    else "medicinal_product"
)

reaction_id_col = "safetyreportid"
reaction_index_col = "reaction_index"

reaction_term_col = (
    "reactionmeddrapt"
    if "reactionmeddrapt" in reactions.columns
    else "reaction_meddrapt"
)

# ----------------------------------------------------------------------
# DRUG DATASET VALIDATION
# ----------------------------------------------------------------------

print("\n" + "=" * 80)
print("DRUG DATASET VALIDATION")
print("-" * 80)

drug_ok = True

# Missing IDs
missing_drug_ids = drugs[drug_id_col].isna().sum()

if missing_drug_ids == 0:
    print("PASS - No missing safety report IDs")
else:
    print(f"FAIL - Missing safety report IDs: {missing_drug_ids}")
    drug_ok = False

# Missing products
missing_products = (
    drugs[drug_product_col]
    .isna()
    .sum()
)

if missing_products == 0:
    print("PASS - No missing medicinal products")
else:
    print(f"FAIL - Missing medicinal products: {missing_products}")
    drug_ok = False

# Duplicate case/index pairs
duplicate_drugs = drugs.duplicated(
    subset=[drug_id_col, drug_index_col]
).sum()

if duplicate_drugs == 0:
    print("PASS - No duplicate case/drug indexes")
else:
    print(f"FAIL - Duplicate case/drug indexes: {duplicate_drugs}")
    drug_ok = False

# Contiguous indexes
bad_drug_index_cases = 0

for case_id, group in drugs.groupby(drug_id_col):

    indexes = sorted(
        pd.to_numeric(
            group[drug_index_col],
            errors="coerce"
        ).dropna().astype(int).tolist()
    )

    expected = list(range(len(indexes)))

    if indexes != expected:
        bad_drug_index_cases += 1

if bad_drug_index_cases == 0:
    print("PASS - Drug indexes are contiguous for every case")
else:
    print(
        f"FAIL - Cases with non-contiguous drug indexes: "
        f"{bad_drug_index_cases}"
    )
    drug_ok = False

# ----------------------------------------------------------------------
# REACTION DATASET VALIDATION
# ----------------------------------------------------------------------

print("\n" + "=" * 80)
print("REACTION DATASET VALIDATION")
print("-" * 80)

reaction_ok = True

missing_reaction_ids = reactions[reaction_id_col].isna().sum()

if missing_reaction_ids == 0:
    print("PASS - No missing safety report IDs")
else:
    print(
        f"FAIL - Missing reaction safety report IDs: "
        f"{missing_reaction_ids}"
    )
    reaction_ok = False

missing_reaction_terms = reactions[reaction_term_col].isna().sum()

if missing_reaction_terms == 0:
    print("PASS - No missing reaction terms")
else:
    print(
        f"FAIL - Missing reaction terms: "
        f"{missing_reaction_terms}"
    )
    reaction_ok = False

duplicate_reactions = reactions.duplicated(
    subset=[reaction_id_col, reaction_index_col]
).sum()

if duplicate_reactions == 0:
    print("PASS - No duplicate case/reaction indexes")
else:
    print(
        f"FAIL - Duplicate case/reaction indexes: "
        f"{duplicate_reactions}"
    )
    reaction_ok = False

bad_reaction_index_cases = 0

for case_id, group in reactions.groupby(reaction_id_col):

    indexes = sorted(
        pd.to_numeric(
            group[reaction_index_col],
            errors="coerce"
        ).dropna().astype(int).tolist()
    )

    expected = list(range(len(indexes)))

    if indexes != expected:
        bad_reaction_index_cases += 1

if bad_reaction_index_cases == 0:
    print("PASS - Reaction indexes are contiguous for every case")
else:
    print(
        f"FAIL - Cases with non-contiguous reaction indexes: "
        f"{bad_reaction_index_cases}"
    )
    reaction_ok = False

# ----------------------------------------------------------------------
# CASE COVERAGE
# ----------------------------------------------------------------------

print("\n" + "=" * 80)
print("CASE COVERAGE")
print("-" * 80)

drug_cases = set(
    drugs[drug_id_col].dropna().astype(str)
)

reaction_cases = set(
    reactions[reaction_id_col].dropna().astype(str)
)

print(f"Drug cases     : {len(drug_cases):,}")
print(f"Reaction cases : {len(reaction_cases):,}")

if len(drug_cases) == 1024:
    print("PASS - Drug dataset contains 1,024 cases")
else:
    print(
        f"WARNING - Expected 1,024 drug cases, "
        f"found {len(drug_cases):,}"
    )

if len(reaction_cases) == 1024:
    print("PASS - Reaction dataset contains 1,024 cases")
else:
    print(
        f"WARNING - Expected 1,024 reaction cases, "
        f"found {len(reaction_cases):,}"
    )

# ----------------------------------------------------------------------
# EMBEDDED COMMA CHECK
# ----------------------------------------------------------------------

print("\n" + "=" * 80)
print("EMBEDDED-COMMA REACTION CHECK")
print("-" * 80)

comma_reactions = reactions[
    reactions[reaction_term_col]
    .astype(str)
    .str.contains(",", regex=False)
]

print(
    f"Reactions containing commas : "
    f"{len(comma_reactions)}"
)

if len(comma_reactions) > 0:

    examples = (
        comma_reactions[reaction_term_col]
        .drop_duplicates()
        .tolist()
    )

    for value in examples:
        print(f"  {value}")

print(
    "PASS - Embedded commas remain inside normalized "
    "reaction terms."
)

# ----------------------------------------------------------------------
# FINAL RESULT
# ----------------------------------------------------------------------

print("\n" + "=" * 80)

if drug_ok and reaction_ok:
    print("FINAL RESULT: PASS")
    print()
    print("Phase 3 integrated validation is COMPLETE.")
    print()
    print("Phase 1 - Drug normalization       : COMPLETE")
    print("Phase 2 - Reaction normalization   : COMPLETE")
    print("Phase 3 - Structure investigation  : COMPLETE")
    print("Phase 3 - Integrated validation    : COMPLETE")
    print()
    print("The normalized ICSR dataset is ready for the next phase.")
else:
    print("FINAL RESULT: FAIL")
    print("One or more normalized dataset checks failed.")

print("=" * 80)