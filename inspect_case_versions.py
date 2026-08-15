from pathlib import Path

import pandas as pd


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

df = pd.read_excel(DATA_FILE)


# --------------------------------------------------
# Find repeated cases
# --------------------------------------------------

case_counts = df["safetyreportid"].value_counts()

repeated_case_ids = case_counts[
    case_counts > 1
].index


# --------------------------------------------------
# Version analysis
# --------------------------------------------------

print("=" * 70)
print("REPEATED CASE VERSION ANALYSIS")
print("=" * 70)

print(
    f"\nRepeated cases: "
    f"{len(repeated_case_ids)}"
)


for case_id in repeated_case_ids:

    case_rows = df[
        df["safetyreportid"] == case_id
    ].copy()

    print("\n" + "-" * 70)

    print(f"CASE ID: {case_id}")

    print(
        case_rows[
            [
                "safetyreportid",
                "safetyreportversion",
                "receivedate",
                "report_date",
                "transmissiondate",
                "primarysourcecountry",
                "occurcountry",
            ]
        ].to_string(index=False)
    )


print("\n" + "=" * 70)
print("VERSION ANALYSIS COMPLETE")
print("=" * 70)