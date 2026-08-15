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


REACTION_COLUMN = (
    "patient_reaction_reactionmeddrapt"
)

OUTCOME_COLUMN = (
    "patient_reaction_reactionoutcome"
)


# --------------------------------------------------
# Cases with mismatches
# --------------------------------------------------

TARGET_CASES = [
    25459724,
    25282743,
    25187835,
    25517207,
    26115793,
    26144528,
]


print("=" * 80)
print("RAW REACTION / OUTCOME CELL INSPECTION")
print("=" * 80)


for case_id in TARGET_CASES:

    case_rows = df[
        df["safetyreportid"] == case_id
    ]

    print("\n" + "=" * 80)
    print(f"CASE ID: {case_id}")
    print("=" * 80)

    for _, row in case_rows.iterrows():

        reaction_value = row[REACTION_COLUMN]
        outcome_value = row[OUTCOME_COLUMN]

        print(
            "\nSafety report version:",
            row["safetyreportversion"]
        )

        print("\nRAW REACTION VALUE:")
        print(repr(reaction_value))

        print("\nRAW OUTCOME VALUE:")
        print(repr(outcome_value))

        print("\nREACTION VALUE TYPE:")
        print(type(reaction_value).__name__)

        print("\nOUTCOME VALUE TYPE:")
        print(type(outcome_value).__name__)


print("\n" + "=" * 80)
print("RAW CELL INSPECTION COMPLETE")
print("=" * 80)