from pathlib import Path

from src.ingestion.loader import load_excel
from src.ingestion.validator import validate_dataset


# --------------------------------------------------
# Locate dataset
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "Bisoprolol_icsr_sample_1068rows.xlsx"
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

print("=" * 60)
print("DATA INGESTION TEST")
print("=" * 60)

df = load_excel(DATA_FILE)

print(f"\nRows loaded    : {len(df)}")
print(f"Columns loaded : {len(df.columns)}")


# --------------------------------------------------
# Validate dataset
# --------------------------------------------------

print("\n" + "=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)

results = validate_dataset(df)


# --------------------------------------------------
# Required columns
# --------------------------------------------------

required = results["required_columns"]

print("\nREQUIRED COLUMNS")
print("-" * 60)

if required["valid"]:
    print("PASS - All required columns are present.")
else:
    print("FAIL - Missing required columns:")
    for column in required["missing"]:
        print(f"  - {column}")


# --------------------------------------------------
# Case IDs
# --------------------------------------------------

cases = results["case_ids"]

print("\nCASE ID VALIDATION")
print("-" * 60)

print(f"Total rows      : {cases['total_rows']}")
print(f"Unique cases    : {cases['unique_cases']}")
print(f"Missing case IDs: {cases['missing_case_ids']}")

if cases["valid"]:
    print("PASS - All rows have a case ID.")
else:
    print("FAIL - Some rows are missing case IDs.")


# --------------------------------------------------
# Seriousness
# --------------------------------------------------

seriousness = results["seriousness"]

print("\nSERIOUSNESS VALIDATION")
print("-" * 60)

print(
    "Values found:",
    seriousness["values_found"]
)

if seriousness["valid"]:
    print("PASS - Seriousness data is present.")
else:
    print("FAIL - Seriousness validation failed.")


print("\n" + "=" * 60)
print("INGESTION TEST COMPLETE")
print("=" * 60)