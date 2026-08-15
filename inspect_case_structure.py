from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Locate project and dataset
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

print("=" * 70)
print("ICSR CASE STRUCTURE INVESTIGATION")
print("=" * 70)

df = pd.read_excel(DATA_FILE)

print(f"\nTotal rows        : {len(df)}")
print(
    f"Unique safety cases: "
    f"{df['safetyreportid'].nunique()}"
)


# --------------------------------------------------
# Find cases appearing more than once
# --------------------------------------------------

case_counts = (
    df["safetyreportid"]
    .value_counts()
    .sort_values(ascending=False)
)


repeated_cases = case_counts[
    case_counts > 1
]


print("\n" + "=" * 70)
print("REPEATED CASES")
print("=" * 70)

print(
    f"\nCases appearing more than once: "
    f"{len(repeated_cases)}"
)

print(
    f"Rows belonging to repeated cases: "
    f"{repeated_cases.sum()}"
)


# --------------------------------------------------
# Distribution of rows per case
# --------------------------------------------------

print("\n" + "=" * 70)
print("ROWS PER CASE DISTRIBUTION")
print("=" * 70)

print(
    case_counts.value_counts()
    .sort_index()
)


# --------------------------------------------------
# Show first repeated case
# --------------------------------------------------

if len(repeated_cases) > 0:

    first_case_id = repeated_cases.index[0]

    print("\n" + "=" * 70)
    print("FIRST REPEATED CASE")
    print("=" * 70)

    print(f"\nCase ID: {first_case_id}")

    case_rows = df[
        df["safetyreportid"] == first_case_id
    ]

    print(
        f"Number of rows for this case: "
        f"{len(case_rows)}"
    )

    print("\nSelected fields:")

    columns_to_show = [
        "safetyreportid",
        "serious",
        "occurcountry",
        "receivedate",
        "patient_patientonsetage",
        "patient_patientsex",
        "patient_reaction_reactionmeddrapt",
        "patient_reaction_reactionoutcome",
        "patient_drug_medicinalproduct",
        "patient_drug_drugcharacterization",
        "patient_drug_drugindication",
        "patient_drug_actiondrug",
    ]

    existing_columns = [
        column
        for column in columns_to_show
        if column in case_rows.columns
    ]

    print(
        case_rows[existing_columns]
        .to_string(index=False)
    )


# --------------------------------------------------
# Check whether repeated rows differ in reactions
# --------------------------------------------------

print("\n" + "=" * 70)
print("REACTION ANALYSIS FOR REPEATED CASES")
print("=" * 70)

if len(repeated_cases) > 0:

    reaction_summary = []

    for case_id in repeated_cases.index:

        case_rows = df[
            df["safetyreportid"] == case_id
        ]

        reactions = (
            case_rows[
                "patient_reaction_reactionmeddrapt"
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        reaction_summary.append(
            {
                "case_id": case_id,
                "row_count": len(case_rows),
                "unique_reactions": len(reactions),
                "reactions": reactions,
            }
        )

    reaction_summary_df = pd.DataFrame(
        reaction_summary
    )

    print(
        reaction_summary_df
        .head(20)
        .to_string(index=False)
    )


# --------------------------------------------------
# Final message
# --------------------------------------------------

print("\n" + "=" * 70)
print("CASE STRUCTURE INVESTIGATION COMPLETE")
print("=" * 70)