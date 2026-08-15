from pathlib import Path

from src.ingestion.loader import load_excel
from src.normalization.versions import (
    select_latest_versions,
)
from src.normalization.reactions import (
    split_reaction_values,
    split_outcome_values,
    normalize_reactions,
    REACTION_COLUMN,
    OUTCOME_COLUMN,
)


# --------------------------------------------------
# Load data
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "Bisoprolol_icsr_sample_1068rows.xlsx"
)

df = load_excel(DATA_FILE)


# --------------------------------------------------
# Use latest case versions
# --------------------------------------------------

latest_df = select_latest_versions(df)


# --------------------------------------------------
# Test known problematic cases
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
print("REACTION NORMALIZATION TEST")
print("=" * 80)


for case_id in TARGET_CASES:

    row = latest_df[
        latest_df["safetyreportid"] == case_id
    ].iloc[0]

    reactions = split_reaction_values(
        row[REACTION_COLUMN]
    )

    outcomes = split_outcome_values(
        row[OUTCOME_COLUMN]
    )

    normalized = normalize_reactions(row)

    print("\n" + "-" * 80)

    print(f"CASE ID: {case_id}")

    print(
        f"Reaction count: {len(reactions)}"
    )

    print(
        f"Outcome count : {len(outcomes)}"
    )

    print("\nNormalized reactions:")

    for index, item in enumerate(
        normalized,
        start=1,
    ):

        print(
            f"  {index}. "
            f"{item['term']} "
            f"→ "
            f"{item['outcome']}"
        )


# --------------------------------------------------
# Global validation
# --------------------------------------------------

print("\n" + "=" * 80)
print("GLOBAL REACTION VALIDATION")
print("=" * 80)


total_reactions = 0
missing_outcomes = 0


for _, row in latest_df.iterrows():

    normalized = normalize_reactions(row)

    total_reactions += len(normalized)

    missing_outcomes += sum(
        item["outcome_missing"]
        for item in normalized
    )


print(
    f"\nTotal normalized reactions: "
    f"{total_reactions}"
)

print(
    f"Reactions with missing outcomes: "
    f"{missing_outcomes}"
)


# --------------------------------------------------
# Final status
# --------------------------------------------------

print("\n" + "=" * 80)
print("REACTION NORMALIZATION TEST COMPLETE")
print("=" * 80)