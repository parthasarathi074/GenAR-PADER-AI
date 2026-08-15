from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "Bisoprolol_icsr_sample_1068rows.xlsx"
)


DRUG_COLUMNS = {
    "characterization":
        "patient_drug_drugcharacterization",

    "medicinal_product":
        "patient_drug_medicinalproduct",

    "authorization_number":
        "patient_drug_drugauthorizationnumb",

    "structured_dose_number":
        "patient_drug_drugstructuredosagenumb",

    "structured_dose_unit":
        "patient_drug_drugstructuredosageunit",

    "separated_dose_number":
        "patient_drug_drugseparatedosagenumb",

    "interval_dose_number":
        "patient_drug_drugintervaldosageunitnumb",

    "interval_dose_definition":
        "patient_drug_drugintervaldosagedefinition",

    "dose_text":
        "patient_drug_drugdosagetext",

    "dosage_form":
        "patient_drug_drugdosageform",

    "administration_route":
        "patient_drug_drugadministrationroute",

    "indication":
        "patient_drug_drugindication",

    "action_taken":
        "patient_drug_actiondrug",

    "additional":
        "patient_drug_drugadditional",

    "active_substance":
        "patient_drug_activesubstance_activesubstancename",

    "start_date_format":
        "patient_drug_drugstartdateformat",

    "start_date":
        "patient_drug_drugstartdate",

    "end_date_format":
        "patient_drug_drugenddateformat",

    "end_date":
        "patient_drug_drugenddate",

    "treatment_duration":
        "patient_drug_drugtreatmentduration",

    "treatment_duration_unit":
        "patient_drug_drugtreatmentdurationunit",

    "cumulative_dose_number":
        "patient_drug_drugcumulativedosagenumb",

    "cumulative_dose_unit":
        "patient_drug_drugcumulativedosageunit",

    "rechallenge":
        "patient_drug_drugrecurreadministration",

    "batch_number":
        "patient_drug_drugbatchnumb",
}


def split_values(value):
    """
    Split a comma-separated cell only for investigation.

    This function is NOT the final parser.
    """

    if pd.isna(value):
        return []

    text = str(value).strip()

    if not text:
        return []

    return [
        item.strip()
        for item in text.split(",")
        if item.strip()
    ]


def describe_row(row):

    print("\n" + "=" * 100)

    print(
        "CASE ID:",
        row["safetyreportid"]
    )

    print(
        "SAFETY VERSION:",
        row["safetyreportversion"]
    )

    print("=" * 100)

    for name, column in DRUG_COLUMNS.items():

        values = split_values(row[column])

        print(
            f"{name:30s}"
            f" count={len(values):2d}"
            f" value={repr(row[column])}"
        )


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 100)
print("DRUG FIELD ALIGNMENT INVESTIGATION")
print("=" * 100)

df = pd.read_excel(DATA_FILE)


# ============================================================
# SELECT LATEST VERSION
# ============================================================

df = (
    df.sort_values(
        [
            "safetyreportid",
            "safetyreportversion",
        ]
    )
    .groupby(
        "safetyreportid",
        as_index=False,
    )
    .tail(1)
    .reset_index(drop=True)
)


print("\nLatest cases:", len(df))


# ============================================================
# IMPORTANT TEST CASES
# ============================================================

TARGET_CASES = [
    24780403,
    24780599,
    24780680,
    24784989,
    24787006,
    24787240,
    26202882,
    26203219,
    26203300,
]


for case_id in TARGET_CASES:

    matching = df[
        df["safetyreportid"] == case_id
    ]

    if matching.empty:

        print(
            f"\nCase {case_id} not found."
        )

        continue

    row = matching.iloc[0]

    describe_row(row)


# ============================================================
# FIELD LENGTH STATISTICS
# ============================================================

print("\n" + "=" * 100)
print("FIELD LENGTH STATISTICS")
print("=" * 100)

statistics = []


for name, column in DRUG_COLUMNS.items():

    counts = (
        df[column]
        .apply(
            lambda value: len(
                split_values(value)
            )
        )
    )

    statistics.append(
        {
            "field": name,
            "rows_with_values": int(
                (counts > 0).sum()
            ),
            "max_values_in_cell": int(
                counts.max()
            ),
            "mean_values": round(
                counts[counts > 0].mean(),
                2
            )
            if (counts > 0).any()
            else 0,
        }
    )


stats_df = pd.DataFrame(statistics)

print(
    stats_df.to_string(
        index=False
    )
)


# ============================================================
# PRODUCT / CHARACTERIZATION / ACTIVE ALIGNMENT
# ============================================================

print("\n" + "=" * 100)
print("CORE DRUG FIELD ALIGNMENT")
print("=" * 100)


CORE_FIELDS = {
    "medicinal_product":
        "patient_drug_medicinalproduct",

    "active_substance":
        "patient_drug_activesubstance_activesubstancename",

    "characterization":
        "patient_drug_drugcharacterization",

    "indication":
        "patient_drug_drugindication",

    "action_taken":
        "patient_drug_actiondrug",
}


alignment_counts = {
    name: 0
    for name in CORE_FIELDS
}


total_cases = len(df)


for _, row in df.iterrows():

    product_values = split_values(
        row[
            CORE_FIELDS["medicinal_product"]
        ]
    )

    product_count = len(
        product_values
    )

    if product_count == 0:
        continue

    for name, column in CORE_FIELDS.items():

        values = split_values(
            row[column]
        )

        if len(values) == product_count:

            alignment_counts[name] += 1


print(
    "\nCases where field count matches "
    "medicinal-product count:"
)

for name, count in alignment_counts.items():

    print(
        f"{name:25s}: "
        f"{count} / {total_cases}"
    )


print("\n" + "=" * 100)
print("DRUG FIELD ALIGNMENT INVESTIGATION COMPLETE")
print("=" * 100)