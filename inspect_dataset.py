import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. Locate dataset
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "Bisoprolol_icsr_sample_1068rows.xlsx"
)


# --------------------------------------------------
# 2. Load dataset
# --------------------------------------------------

print("=" * 60)
print("LOADING DATASET")
print("=" * 60)

df = pd.read_excel(DATA_FILE)


# --------------------------------------------------
# 3. Basic information
# --------------------------------------------------

print("\nDATASET SHAPE")
print("-" * 60)

print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")


# --------------------------------------------------
# 4. Column names
# --------------------------------------------------

print("\nCOLUMN NAMES")
print("-" * 60)

for index, column in enumerate(df.columns, start=1):
    print(f"{index:3}. {column}")


# --------------------------------------------------
# 5. First five rows
# --------------------------------------------------

print("\nFIRST 5 ROWS")
print("-" * 60)

print(df.head())


# --------------------------------------------------
# 6. Data types
# --------------------------------------------------

print("\nDATA TYPES")
print("-" * 60)

print(df.dtypes)


# --------------------------------------------------
# 7. Missing values
# --------------------------------------------------

print("\nMISSING VALUES")
print("-" * 60)

missing = df.isnull().sum()

missing = missing[missing > 0].sort_values(ascending=False)

print(missing)


# --------------------------------------------------
# 8. Duplicate rows
# --------------------------------------------------

print("\nDUPLICATE ROWS")
print("-" * 60)

print(f"Duplicate rows: {df.duplicated().sum()}")


# --------------------------------------------------
# 9. Unique safety report IDs
# --------------------------------------------------

print("\nUNIQUE SAFETY REPORT IDs")
print("-" * 60)

if "safetyreportid" in df.columns:
    print(
        f"Unique cases: "
        f"{df['safetyreportid'].nunique()}"
    )
else:
    print("safetyreportid column not found.")


print("\n" + "=" * 60)
print("DATASET INSPECTION COMPLETE")
print("=" * 60)