from pathlib import Path

from src.ingestion.loader import load_excel
from src.normalization.versions import (
    select_latest_versions,
)


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
# Load raw dataset
# --------------------------------------------------

print("=" * 70)
print("VERSION NORMALIZATION TEST")
print("=" * 70)

df = load_excel(DATA_FILE)

print(f"\nRaw rows           : {len(df)}")
print(
    f"Raw unique cases  : "
    f"{df['safetyreportid'].nunique()}"
)


# --------------------------------------------------
# Select latest versions
# --------------------------------------------------

latest_df = select_latest_versions(df)


print("\n" + "=" * 70)
print("LATEST VERSION RESULTS")
print("=" * 70)

print(
    f"\nNormalized rows    : {len(latest_df)}"
)

print(
    f"Unique case IDs    : "
    f"{latest_df['safetyreportid'].nunique()}"
)


# --------------------------------------------------
# Check that every case appears once
# --------------------------------------------------

duplicate_case_ids = (
    latest_df["safetyreportid"]
    .duplicated()
    .sum()
)


print(
    f"Duplicate case IDs : "
    f"{duplicate_case_ids}"
)


# --------------------------------------------------
# Validation
# --------------------------------------------------

print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)

if len(latest_df) == df["safetyreportid"].nunique():
    print(
        "PASS - One latest record exists "
        "for every safety case."
    )
else:
    print(
        "FAIL - Number of normalized records "
        "does not match unique cases."
    )


if duplicate_case_ids == 0:
    print(
        "PASS - No duplicate safetyreportid "
        "values remain."
    )
else:
    print(
        "FAIL - Duplicate safetyreportid "
        "values remain."
    )


# --------------------------------------------------
# Display repeated cases
# --------------------------------------------------

print("\n" + "=" * 70)
print("SAMPLE LATEST VERSIONS")
print("=" * 70)

repeated_case_ids = (
    df["safetyreportid"]
    .value_counts()
)

repeated_case_ids = repeated_case_ids[
    repeated_case_ids > 1
].index


sample_ids = repeated_case_ids[:10]

print(
    latest_df[
        latest_df["safetyreportid"]
        .isin(sample_ids)
    ][
        [
            "safetyreportid",
            "safetyreportversion",
        ]
    ]
    .sort_values("safetyreportid")
    .to_string(index=False)
)


print("\n" + "=" * 70)
print("VERSION NORMALIZATION TEST COMPLETE")
print("=" * 70)