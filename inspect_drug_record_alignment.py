import pandas as pd
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = Path("data/Bisoprolol_icsr_sample_1068rows.xlsx")

# Cases we want to investigate
CASE_IDS = [
    24780403,
    24780599,
    24780680,
    25571836,
    25829019,
    25858101,
]

# Actual column names in the Excel dataset
CASE_ID_COL = "safetyreportid"
VERSION_COL = "safetyreportversion"

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

    "separate_dose_number":
        "patient_drug_drugseparatedosagenumb",

    "interval_dose_number":
        "patient_drug_drugintervaldosageunitnumb",

    "interval_definition":
        "patient_drug_drugintervaldosagedefinition",

    "dose_text":
        "patient_drug_drugdosagetext",

    "dosage_form":
        "patient_drug_drugdosageform",

    "administration_route":
        "patient_drug_drugadministrationroute",

    "indication":
        "patient_drug_drugindication",

    "action":
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


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    print("Loading dataset...")
    print(f"Path: {DATA_PATH}")

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    df = pd.read_excel(
        DATA_PATH,
        engine="openpyxl"
    )

    print(f"Raw rows : {len(df)}")
    print(f"Columns  : {len(df.columns)}")

    # --------------------------------------------------------
    # Validate required columns
    # --------------------------------------------------------

    required = [
        CASE_ID_COL,
        VERSION_COL,
    ]

    missing = [
        col for col in required
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Required columns missing: {missing}\n"
            f"Available columns:\n{list(df.columns)}"
        )

    return df


# ============================================================
# KEEP LATEST VERSION
# ============================================================

def latest_versions(df):

    print()
    print("Keeping latest safety report version...")

    work = df.copy()

    # Convert IDs to numeric
    work[CASE_ID_COL] = pd.to_numeric(
        work[CASE_ID_COL],
        errors="coerce"
    )

    work[VERSION_COL] = pd.to_numeric(
        work[VERSION_COL],
        errors="coerce"
    )

    # Remove rows without case ID
    work = work.dropna(
        subset=[CASE_ID_COL]
    )

    # If version is missing, treat it as 0
    work[VERSION_COL] = work[VERSION_COL].fillna(0)

    # Sort by case + version
    work = work.sort_values(
        [CASE_ID_COL, VERSION_COL]
    )

    # Keep highest version for every case
    latest = (
        work
        .groupby(CASE_ID_COL, as_index=False)
        .tail(1)
        .copy()
    )

    latest = latest.sort_values(
        CASE_ID_COL
    )

    print(f"Latest rows : {len(latest)}")
    print(
        f"Unique cases: "
        f"{latest[CASE_ID_COL].nunique()}"
    )

    return latest


# ============================================================
# HELPER
# ============================================================

def clean_value(value):

    if pd.isna(value):
        return ""

    text = str(value).strip()

    if text.lower() in {
        "nan",
        "none",
        "null",
        ""
    }:
        return ""

    return text


# ============================================================
# EXTRACT DRUG LIST
# ============================================================

def get_drug_count(row):

    product_col = DRUG_COLUMNS["medicinal_product"]

    if product_col not in row.index:
        return 0

    value = clean_value(row[product_col])

    if not value:
        return 0

    # The dataset stores repeated drug values
    # as comma-separated strings.
    return len([
        x for x in value.split(",")
        if x.strip()
    ])


# ============================================================
# PRINT DRUG RECORD
# ============================================================

def print_drug_record(row, index):

    print()
    print(f"Drug {index}")

    print(
        f"  Medicinal product : "
        f"{clean_value(row[DRUG_COLUMNS['medicinal_product']])}"
    )

    print(
        f"  Characterization  : "
        f"{clean_value(row[DRUG_COLUMNS['characterization']])}"
    )

    print(
        f"  Active substance  : "
        f"{clean_value(row[DRUG_COLUMNS['active_substance']])}"
    )

    print(
        f"  Route             : "
        f"{clean_value(row[DRUG_COLUMNS['administration_route']])}"
    )

    print(
        f"  Indication        : "
        f"{clean_value(row[DRUG_COLUMNS['indication']])}"
    )

    print(
        f"  Action taken      : "
        f"{clean_value(row[DRUG_COLUMNS['action']])}"
    )

    print(
        f"  Dose text         : "
        f"{clean_value(row[DRUG_COLUMNS['dose_text']])}"
    )

    print(
        f"  Dosage form       : "
        f"{clean_value(row[DRUG_COLUMNS['dosage_form']])}"
    )


# ============================================================
# INVESTIGATE CASE
# ============================================================

def investigate_case(row):

    case_id = int(row[CASE_ID_COL])
    version = int(row[VERSION_COL])

    print()
    print("=" * 100)
    print(f"CASE ID: {case_id}")
    print(f"SAFETY VERSION: {version}")
    print("=" * 100)

    # --------------------------------------------------------
    # General case information
    # --------------------------------------------------------

    print()
    print("CASE INFORMATION")
    print("-" * 100)

    general_columns = [
        "safetyreportid",
        "safetyreportversion",
        "receivedate",
        "report_date",
        "transmissiondate",
        "primarysourcecountry",
        "occurcountry",
        "reporttype",
        "serious",
        "seriousnessdeath",
        "seriousnesslifethreatening",
        "seriousnesshospitalization",
        "patient_patientsex",
        "patient_patientonsetage",
        "patient_patientonsetageunit",
    ]

    for col in general_columns:

        if col in row.index:

            print(
                f"{col:<45}: "
                f"{clean_value(row[col])}"
            )

    # --------------------------------------------------------
    # Drug fields
    # --------------------------------------------------------

    print()
    print("RAW DRUG FIELDS")
    print("-" * 100)

    for key, column in DRUG_COLUMNS.items():

        if column in row.index:

            value = clean_value(row[column])

            print(
                f"{key:<30}: "
                f"{value}"
            )

    # --------------------------------------------------------
    # Drug count
    # --------------------------------------------------------

    drug_count = get_drug_count(row)

    print()
    print("DRUG COUNT")
    print("-" * 100)
    print(
        f"Estimated drug records : {drug_count}"
    )


# ============================================================
# ALIGNMENT INVESTIGATION
# ============================================================

def investigate_alignment(latest):

    print()
    print("=" * 100)
    print("SELECTED CASE INVESTIGATION")
    print("=" * 100)

    available_cases = set(
        pd.to_numeric(
            latest[CASE_ID_COL],
            errors="coerce"
        )
        .dropna()
        .astype(int)
    )

    for case_id in CASE_IDS:

        print()

        if case_id not in available_cases:

            print("=" * 100)
            print(
                f"CASE ID {case_id} NOT FOUND"
            )
            print("=" * 100)

            continue

        matching = latest[
            pd.to_numeric(
                latest[CASE_ID_COL],
                errors="coerce"
            ) == case_id
        ]

        for _, row in matching.iterrows():

            investigate_case(row)


# ============================================================
# DATASET VALIDATION
# ============================================================

def validate_dataset(latest):

    print()
    print("=" * 100)
    print("DATASET VALIDATION")
    print("=" * 100)

    print()
    print("CASE STATISTICS")
    print("-" * 100)

    print(
        f"Latest case rows      : {len(latest)}"
    )

    print(
        f"Unique case IDs       : "
        f"{latest[CASE_ID_COL].nunique()}"
    )

    print(
        f"Minimum version      : "
        f"{latest[VERSION_COL].min()}"
    )

    print(
        f"Maximum version      : "
        f"{latest[VERSION_COL].max()}"
    )

    # --------------------------------------------------------
    # Drug product availability
    # --------------------------------------------------------

    product_col = DRUG_COLUMNS["medicinal_product"]

    missing_products = (
        latest[product_col]
        .isna()
        .sum()
    )

    print()
    print("MEDICINAL PRODUCT VALIDATION")
    print("-" * 100)

    print(
        f"Rows missing product field : "
        f"{missing_products}"
    )

    if missing_products == 0:

        print(
            "PASS - Every latest case has "
            "a medicinal product field."
        )

    else:

        print(
            "WARNING - Some latest cases "
            "have missing medicinal products."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 100)
    print("DRUG RECORD ALIGNMENT INVESTIGATION")
    print("=" * 100)

    df = load_dataset()

    latest = latest_versions(df)

    validate_dataset(latest)

    investigate_alignment(latest)

    print()
    print("=" * 100)
    print("DRUG RECORD ALIGNMENT INVESTIGATION COMPLETE")
    print("=" * 100)


if __name__ == "__main__":
    main()