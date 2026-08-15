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
# Helper function
# --------------------------------------------------

def split_values(value):
    """
    Split a comma-separated field into individual
    values while handling missing data.
    """

    if pd.isna(value):
        return []

    return [
        item.strip()
        for item in str(value).split(",")
        if item.strip()
    ]


# --------------------------------------------------
# Analyze reaction fields
# --------------------------------------------------

print("=" * 70)
print("REACTION STRUCTURE INVESTIGATION")
print("=" * 70)


reaction_column = (
    "patient_reaction_reactionmeddrapt"
)

outcome_column = (
    "patient_reaction_reactionoutcome"
)


reaction_counts = []
outcome_counts = []


for _, row in df.iterrows():

    reactions = split_values(
        row[reaction_column]
    )

    outcomes = split_values(
        row[outcome_column]
    )

    reaction_counts.append(len(reactions))
    outcome_counts.append(len(outcomes))


# --------------------------------------------------
# Basic statistics
# --------------------------------------------------

print("\nREACTION COUNTS PER ROW")
print("-" * 70)

reaction_distribution = (
    pd.Series(reaction_counts)
    .value_counts()
    .sort_index()
)

print(reaction_distribution.to_string())


print("\nOUTCOME COUNTS PER ROW")
print("-" * 70)

outcome_distribution = (
    pd.Series(outcome_counts)
    .value_counts()
    .sort_index()
)

print(outcome_distribution.to_string())


# --------------------------------------------------
# Find rows with multiple reactions
# --------------------------------------------------

multi_reaction_rows = df[
    df[reaction_column]
    .fillna("")
    .astype(str)
    .str.contains(",")
]


print("\n" + "=" * 70)
print("MULTI-REACTION EXAMPLES")
print("=" * 70)

print(
    f"\nRows containing multiple reactions: "
    f"{len(multi_reaction_rows)}"
)


for _, row in multi_reaction_rows.head(10).iterrows():

    reactions = split_values(
        row[reaction_column]
    )

    outcomes = split_values(
        row[outcome_column]
    )

    print("\nCase ID:", row["safetyreportid"])

    print("Reactions:")
    for index, reaction in enumerate(
        reactions,
        start=1,
    ):
        print(f"  {index}. {reaction}")

    print("Outcomes:")
    for index, outcome in enumerate(
        outcomes,
        start=1,
    ):
        print(f"  {index}. {outcome}")

    print(
        f"Reaction count : {len(reactions)}"
    )

    print(
        f"Outcome count  : {len(outcomes)}"
    )


# --------------------------------------------------
# Check alignment
# --------------------------------------------------

print("\n" + "=" * 70)
print("REACTION / OUTCOME ALIGNMENT")
print("=" * 70)


alignment_counts = {
    "same": 0,
    "different": 0,
}


for _, row in df.iterrows():

    reactions = split_values(
        row[reaction_column]
    )

    outcomes = split_values(
        row[outcome_column]
    )

    if len(reactions) == len(outcomes):
        alignment_counts["same"] += 1
    else:
        alignment_counts["different"] += 1


print(
    f"Matching reaction/outcome counts   : "
    f"{alignment_counts['same']}"
)

print(
    f"Different reaction/outcome counts   : "
    f"{alignment_counts['different']}"
)


print("\n" + "=" * 70)
print("REACTION STRUCTURE INVESTIGATION COMPLETE")
print("=" * 70)