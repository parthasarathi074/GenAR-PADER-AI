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
# Columns we want to compare
# --------------------------------------------------

COMPARISON_COLUMNS = [
    "safetyreportversion",
    "receivedate",
    "report_date",
    "transmissiondate",
    "serious",
    "primarysourcecountry",
    "occurcountry",
    "patient_patientonsetage",
    "patient_patientonsetageunit",
    "patient_patientsex",
    "patient_reaction_reactionmeddrapt",
    "patient_reaction_reactionoutcome",
    "patient_drug_medicinalproduct",
    "patient_drug_drugcharacterization",
    "patient_drug_drugindication",
    "patient_drug_actiondrug",
    "patient_drug_activesubstance_activesubstancename",
]


# --------------------------------------------------
# Find repeated cases
# --------------------------------------------------

case_counts = df["safetyreportid"].value_counts()

repeated_case_ids = case_counts[
    case_counts > 1
].index


print("=" * 80)
print("CASE VERSION COMPLETENESS ANALYSIS")
print("=" * 80)

print(
    f"\nRepeated cases found: "
    f"{len(repeated_case_ids)}"
)


# --------------------------------------------------
# Compare each repeated case
# --------------------------------------------------

for case_id in repeated_case_ids:

    case_rows = df[
        df["safetyreportid"] == case_id
    ].copy()

    case_rows = case_rows.sort_values(
        "safetyreportversion"
    )

    latest_version = case_rows[
        "safetyreportversion"
    ].max()

    latest_row = case_rows[
        case_rows["safetyreportversion"]
        == latest_version
    ].iloc[0]

    print("\n" + "=" * 80)
    print(f"CASE ID: {case_id}")
    print(f"Versions: {case_rows['safetyreportversion'].tolist()}")
    print(f"Latest version: {latest_version}")
    print("=" * 80)

    # ----------------------------------------------
    # Compare important fields
    # ----------------------------------------------

    for column in COMPARISON_COLUMNS:

        if column == "safetyreportversion":
            continue

        values = []

        for value in case_rows[column]:

            if pd.isna(value):
                normalized = "<MISSING>"
            else:
                normalized = str(value).strip()

            if normalized not in values:
                values.append(normalized)

        if len(values) > 1:

            print(f"\nCHANGED: {column}")

            for value in values:
                print(f"  - {value}")


    # ----------------------------------------------
    # Reaction comparison
    # ----------------------------------------------

    print("\nREACTIONS BY VERSION")

    for _, row in case_rows.iterrows():

        version = row["safetyreportversion"]

        reaction_value = row[
            "patient_reaction_reactionmeddrapt"
        ]

        if pd.isna(reaction_value):
            reaction_value = "<MISSING>"

        print(
            f"  Version {version}: "
            f"{reaction_value}"
        )


    # ----------------------------------------------
    # Drug comparison
    # ----------------------------------------------

    print("\nDRUGS BY VERSION")

    for _, row in case_rows.iterrows():

        version = row["safetyreportversion"]

        drug_value = row[
            "patient_drug_medicinalproduct"
        ]

        if pd.isna(drug_value):
            drug_value = "<MISSING>"

        print(
            f"  Version {version}: "
            f"{drug_value}"
        )


print("\n" + "=" * 80)
print("VERSION COMPLETENESS ANALYSIS COMPLETE")
print("=" * 80)