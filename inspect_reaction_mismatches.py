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
# Helper
# --------------------------------------------------

def split_values(value):

    if pd.isna(value):
        return []

    return [
        item.strip()
        for item in str(value).split(",")
        if item.strip()
    ]


# --------------------------------------------------
# Find mismatches
# --------------------------------------------------

mismatches = []


for _, row in df.iterrows():

    reactions = split_values(
        row[REACTION_COLUMN]
    )

    outcomes = split_values(
        row[OUTCOME_COLUMN]
    )

    if len(reactions) != len(outcomes):

        mismatches.append(
            {
                "case_id": row["safetyreportid"],
                "version": row["safetyreportversion"],
                "reaction_count": len(reactions),
                "outcome_count": len(outcomes),
                "reactions": reactions,
                "outcomes": outcomes,
            }
        )


# --------------------------------------------------
# Display mismatches
# --------------------------------------------------

print("=" * 80)
print("REACTION / OUTCOME MISMATCH ANALYSIS")
print("=" * 80)

print(
    f"\nMismatched rows: {len(mismatches)}"
)


for item in mismatches:

    print("\n" + "-" * 80)

    print(
        f"Case ID          : "
        f"{item['case_id']}"
    )

    print(
        f"Safety version   : "
        f"{item['version']}"
    )

    print(
        f"Reaction count   : "
        f"{item['reaction_count']}"
    )

    print(
        f"Outcome count    : "
        f"{item['outcome_count']}"
    )

    print("\nReactions:")

    for index, reaction in enumerate(
        item["reactions"],
        start=1,
    ):
        print(
            f"  {index}. {reaction}"
        )

    print("\nOutcomes:")

    for index, outcome in enumerate(
        item["outcomes"],
        start=1,
    ):
        print(
            f"  {index}. {outcome}"
        )


print("\n" + "=" * 80)
print("MISMATCH ANALYSIS COMPLETE")
print("=" * 80)