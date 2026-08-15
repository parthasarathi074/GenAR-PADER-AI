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
# Drug columns
# --------------------------------------------------

DRUG_COLUMNS = [
    "patient_drug_drugcharacterization",
    "patient_drug_medicinalproduct",
    "patient_drug_drugauthorizationnumb",
    "patient_drug_drugstructuredosagenumb",
    "patient_drug_drugstructuredosageunit",
    "patient_drug_drugseparatedosagenumb",
    "patient_drug_drugintervaldosageunitnumb",
    "patient_drug_drugintervaldosagedefinition",
    "patient_drug_drugdosagetext",
    "patient_drug_drugdosageform",
    "patient_drug_drugadministrationroute",
    "patient_drug_drugindication",
    "patient_drug_actiondrug",
    "patient_drug_drugadditional",
    "patient_drug_activesubstance_activesubstancename",
    "patient_drug_drugstartdateformat",
    "patient_drug_drugstartdate",
    "patient_drug_drugenddateformat",
    "patient_drug_drugenddate",
    "patient_drug_drugtreatmentduration",
    "patient_drug_drugtreatmentdurationunit",
    "patient_drug_drugcumulativedosagenumb",
    "patient_drug_drugcumulativedosageunit",
    "patient_drug_drugrecurreadministration",
    "patient_drug_drugbatchnumb",
]


# --------------------------------------------------
# Basic drug availability
# --------------------------------------------------

print("=" * 80)
print("DRUG STRUCTURE INVESTIGATION")
print("=" * 80)


print("\nDATASET ROWS")
print("-" * 80)

print(f"Rows: {len(df)}")


# --------------------------------------------------
# Medicinal product availability
# --------------------------------------------------

medicinal_product = (
    "patient_drug_medicinalproduct"
)

active_substance = (
    "patient_drug_activesubstance_activesubstancename"
)

drug_characterization = (
    "patient_drug_drugcharacterization"
)


print("\nDRUG FIELD AVAILABILITY")
print("-" * 80)

print(
    "Medicinal product populated:",
    df[medicinal_product].notna().sum()
)

print(
    "Active substance populated:",
    df[active_substance].notna().sum()
)

print(
    "Drug characterization populated:",
    df[drug_characterization].notna().sum()
)


# --------------------------------------------------
# Unique medicinal products
# --------------------------------------------------

print("\nUNIQUE MEDICINAL PRODUCTS")
print("-" * 80)

products = (
    df[medicinal_product]
    .dropna()
    .astype(str)
    .str.strip()
)

print(
    f"Unique medicinal products: "
    f"{products.nunique()}"
)

print("\nTop medicinal products:")

print(
    products
    .value_counts()
    .head(20)
    .to_string()
)


# --------------------------------------------------
# Drug characterization
# --------------------------------------------------

print("\nDRUG CHARACTERIZATION")
print("-" * 80)

print(
    df[drug_characterization]
    .value_counts(dropna=False)
    .to_string()
)


# --------------------------------------------------
# Active substances
# --------------------------------------------------

print("\nACTIVE SUBSTANCES")
print("-" * 80)

substances = (
    df[active_substance]
    .dropna()
    .astype(str)
    .str.strip()
)

print(
    f"Unique active substances: "
    f"{substances.nunique()}"
)

print(
    substances
    .value_counts()
    .head(20)
    .to_string()
)


# --------------------------------------------------
# Action taken
# --------------------------------------------------

action_column = "patient_drug_actiondrug"

print("\nACTION TAKEN")
print("-" * 80)

print(
    df[action_column]
    .value_counts(dropna=False)
    .to_string()
)


# --------------------------------------------------
# Administration route
# --------------------------------------------------

route_column = (
    "patient_drug_drugadministrationroute"
)

print("\nADMINISTRATION ROUTE")
print("-" * 80)

print(
    df[route_column]
    .value_counts(dropna=False)
    .head(30)
    .to_string()
)


# --------------------------------------------------
# Dosage form
# --------------------------------------------------

dosage_form_column = (
    "patient_drug_drugdosageform"
)

print("\nDOSAGE FORM")
print("-" * 80)

print(
    df[dosage_form_column]
    .value_counts(dropna=False)
    .head(30)
    .to_string()
)


# --------------------------------------------------
# Indication
# --------------------------------------------------

indication_column = (
    "patient_drug_drugindication"
)

print("\nDRUG INDICATION")
print("-" * 80)

indications = (
    df[indication_column]
    .dropna()
    .astype(str)
    .str.strip()
)

print(
    f"Unique indications: "
    f"{indications.nunique()}"
)

print(
    indications
    .value_counts()
    .head(20)
    .to_string()
)


# --------------------------------------------------
# Rows containing multiple medicinal products
# --------------------------------------------------

print("\nMULTI-VALUE MEDICINAL PRODUCT CELLS")
print("-" * 80)

multi_product_rows = df[
    df[medicinal_product]
    .fillna("")
    .astype(str)
    .str.contains(",")
]

print(
    "Rows containing comma in medicinal product:",
    len(multi_product_rows)
)


# --------------------------------------------------
# Show examples
# --------------------------------------------------

print("\nMULTI-VALUE PRODUCT EXAMPLES")
print("-" * 80)

for _, row in multi_product_rows.head(10).iterrows():

    print(
        "\nCase ID:",
        row["safetyreportid"]
    )

    print(
        "Medicinal product:",
        repr(row[medicinal_product])
    )

    print(
        "Active substance:",
        repr(row[active_substance])
    )

    print(
        "Characterization:",
        repr(row[drug_characterization])
    )


# --------------------------------------------------
# Raw drug rows
# --------------------------------------------------

print("\nRAW DRUG FIELD EXAMPLES")
print("-" * 80)

sample = df[
    [
        "safetyreportid",
        "safetyreportversion",
        medicinal_product,
        active_substance,
        drug_characterization,
        "patient_drug_drugdosagetext",
        route_column,
        indication_column,
        action_column,
    ]
].head(10)

print(
    sample.to_string(index=False)
)


print("\n" + "=" * 80)
print("DRUG STRUCTURE INVESTIGATION COMPLETE")
print("=" * 80) 