import os
import re
import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = os.path.join(
    "data",
    "Bisoprolol_icsr_sample_1068rows.xlsx"
)

OUTPUT_DIR = "data"

NORMALIZED_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "normalized_drugs.csv"
)

ALIGNMENT_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "drug_alignment_report.csv"
)


# ============================================================
# COLUMN MAPPING
# ============================================================

CASE_ID_COL = "safetyreportid"
VERSION_COL = "safetyreportversion"

DRUG_FIELDS = {
    "drug_characterization":
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


CASE_FIELDS = {
    "safetyreportid": "safetyreportid",
    "safetyreportversion": "safetyreportversion",
    "receivedate": "receivedate",
    "report_date": "report_date",
    "transmissiondate": "transmissiondate",
    "primarysourcecountry": "primarysourcecountry",
    "occurcountry": "occurcountry",
    "reporttype": "reporttype",
    "serious": "serious",
    "seriousnessdeath": "seriousnessdeath",
    "seriousnesslifethreatening":
        "seriousnesslifethreatening",
    "seriousnesshospitalization":
        "seriousnesshospitalization",
    "seriousnessdisabling":
        "seriousnessdisabling",
    "patient_sex":
        "patient_patientsex",
    "patient_age":
        "patient_patientonsetage",
    "patient_age_unit":
        "patient_patientonsetageunit",
}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def is_missing(value):
    """
    Detect pandas/Excel missing values and empty strings.
    """
    if value is None:
        return True

    try:
        if pd.isna(value):
            return True
    except Exception:
        pass

    text = str(value).strip()

    return text == "" or text.lower() in {
        "nan",
        "none",
        "null"
    }


def clean_scalar(value):
    """
    Convert a raw Excel value to a clean string/None.
    """
    if is_missing(value):
        return None

    text = str(value).strip()

    return text if text else None


def split_drug_field(value):
    """
    Split a comma-separated drug field while preserving
    empty positions.

    Important:
    We DO NOT remove empty elements because positional
    alignment matters.
    """

    if is_missing(value):
        return []

    text = str(value)

    parts = text.split(",")

    return [
        part.strip() if part.strip() else None
        for part in parts
    ]


def field_length(value):
    """
    Return number of comma-separated elements.
    """
    return len(split_drug_field(value))


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    print("=" * 70)
    print("LOADING DATASET")
    print("=" * 70)

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Dataset not found:\n{DATA_PATH}"
        )

    df = pd.read_excel(
        DATA_PATH,
        engine="openpyxl"
    )

    print(f"Rows loaded    : {len(df)}")
    print(f"Columns loaded : {len(df.columns)}")

    return df


# ============================================================
# VALIDATE SOURCE SCHEMA
# ============================================================

def validate_schema(df):

    required = [
        CASE_ID_COL,
        VERSION_COL
    ]

    required.extend(
        DRUG_FIELDS.values()
    )

    missing = [
        col for col in required
        if col not in df.columns
    ]

    if missing:

        print("\nMissing columns:")

        for col in missing:
            print(f"  - {col}")

        raise ValueError(
            "Required source columns are missing."
        )


# ============================================================
# KEEP LATEST CASE VERSION
# ============================================================

def keep_latest_versions(df):

    print()
    print("=" * 70)
    print("KEEPING LATEST SAFETY REPORT VERSION")
    print("=" * 70)

    work = df.copy()

    work[CASE_ID_COL] = pd.to_numeric(
        work[CASE_ID_COL],
        errors="coerce"
    )

    work[VERSION_COL] = pd.to_numeric(
        work[VERSION_COL],
        errors="coerce"
    )

    before = len(work)

    work = work.dropna(
        subset=[CASE_ID_COL]
    )

    work = (
        work
        .sort_values(
            [CASE_ID_COL, VERSION_COL]
        )
        .drop_duplicates(
            subset=[CASE_ID_COL],
            keep="last"
        )
        .reset_index(drop=True)
    )

    print(f"Raw rows          : {before}")
    print(f"Normalized rows   : {len(work)}")
    print(
        f"Unique case IDs   : "
        f"{work[CASE_ID_COL].nunique()}"
    )

    return work


# ============================================================
# DETERMINE DRUG COUNT
# ============================================================

def determine_drug_count(row):

    """
    The medicinal product field is the primary sequence.

    If it exists, its number of values determines the drug
    record count.

    Other fields are used as supporting evidence.
    """

    product_col = DRUG_FIELDS["medicinal_product"]

    products = split_drug_field(
        row.get(product_col)
    )

    if products:
        return len(products)

    # Fallback:
    lengths = []

    for source_col in DRUG_FIELDS.values():

        values = split_drug_field(
            row.get(source_col)
        )

        if values:
            lengths.append(len(values))

    return max(lengths) if lengths else 0


# ============================================================
# ALIGNMENT ANALYSIS
# ============================================================

def analyze_alignment(row):

    lengths = {}

    for field_name, source_col in DRUG_FIELDS.items():

        lengths[field_name] = field_length(
            row.get(source_col)
        )

    nonzero_lengths = [
        value
        for value in lengths.values()
        if value > 0
    ]

    expected = determine_drug_count(row)

    mismatched = {
        field: length
        for field, length in lengths.items()
        if length not in (0, expected)
    }

    return expected, lengths, mismatched


# ============================================================
# BUILD ONE DRUG RECORD
# ============================================================

def build_drug_record(
    row,
    drug_index,
    drug_count,
    split_cache
):

    record = {}

    # --------------------------------------------------------
    # CASE FIELDS
    # --------------------------------------------------------

    for output_name, source_col in CASE_FIELDS.items():

        value = row.get(source_col)

        if output_name == "report_date":

            if not is_missing(value):

                try:
                    value = pd.to_datetime(
                        value
                    ).strftime("%Y-%m-%d")
                except Exception:
                    value = clean_scalar(value)

            else:
                value = None

        else:
            value = clean_scalar(value)

        record[output_name] = value

    # --------------------------------------------------------
    # DRUG INDEX
    # --------------------------------------------------------

    record["drug_index"] = drug_index
    record["drug_count"] = drug_count

    # --------------------------------------------------------
    # DRUG FIELDS
    # --------------------------------------------------------

    for output_name in DRUG_FIELDS:

        values = split_cache.get(
            output_name,
            []
        )

        if drug_index < len(values):

            value = values[drug_index]

        else:

            value = None

        record[output_name] = clean_scalar(value)

    return record


# ============================================================
# NORMALIZE DRUGS
# ============================================================

def normalize_drugs(df):

    print()
    print("=" * 70)
    print("NORMALIZING DRUG RECORDS")
    print("=" * 70)

    records = []
    alignment_records = []

    for _, row in df.iterrows():

        case_id = int(row[CASE_ID_COL])

        drug_count, lengths, mismatched = (
            analyze_alignment(row)
        )

        # ----------------------------------------------------
        # Prepare split values
        # ----------------------------------------------------

        split_cache = {}

        for field_name, source_col in DRUG_FIELDS.items():

            split_cache[field_name] = (
                split_drug_field(
                    row.get(source_col)
                )
            )

        # ----------------------------------------------------
        # Alignment report
        # ----------------------------------------------------

        alignment_records.append({

            "case_id": case_id,

            "safetyreportversion":
                clean_scalar(
                    row.get(VERSION_COL)
                ),

            "expected_drug_count":
                drug_count,

            "mismatched_field_count":
                len(mismatched),

            "mismatched_fields":
                "; ".join(mismatched.keys()),

            "field_lengths":
                "; ".join(
                    f"{k}={v}"
                    for k, v in lengths.items()
                    if v > 0
                ),

        })

        # ----------------------------------------------------
        # Create drug records
        # ----------------------------------------------------

        for drug_index in range(drug_count):

            record = build_drug_record(
                row=row,
                drug_index=drug_index,
                drug_count=drug_count,
                split_cache=split_cache
            )

            records.append(record)

    normalized = pd.DataFrame(records)

    alignment = pd.DataFrame(
        alignment_records
    )

    return normalized, alignment


# ============================================================
# VALIDATION
# ============================================================

def validate_normalized_data(
    normalized,
    alignment
):

    print()
    print("=" * 70)
    print("DRUG NORMALIZATION VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Total records
    # --------------------------------------------------------

    print()
    print("TOTAL NORMALIZED DRUG RECORDS")
    print("-" * 70)

    print(
        f"Drug records      : "
        f"{len(normalized)}"
    )

    # --------------------------------------------------------
    # Cases
    # --------------------------------------------------------

    print()
    print("UNIQUE CASES")
    print("-" * 70)

    case_count = normalized[
        "safetyreportid"
    ].nunique()

    print(
        f"Cases represented : "
        f"{case_count}"
    )

    # --------------------------------------------------------
    # Missing medicinal products
    # --------------------------------------------------------

    missing_products = normalized[
        normalized["medicinal_product"].isna()
        | (
            normalized["medicinal_product"]
            .astype(str)
            .str.strip()
            .eq("")
        )
    ]

    print()
    print("MISSING MEDICINAL PRODUCTS")
    print("-" * 70)

    print(
        f"Missing products  : "
        f"{len(missing_products)}"
    )

    if len(missing_products) == 0:
        print(
            "PASS - Every normalized drug "
            "has a medicinal product."
        )
    else:
        print(
            "WARNING - Some normalized records "
            "are missing medicinal products."
        )

    # --------------------------------------------------------
    # Drug count per case
    # --------------------------------------------------------

    counts = (
        normalized
        .groupby("safetyreportid")
        .size()
    )

    print()
    print("DRUGS PER CASE")
    print("-" * 70)

    if len(counts):

        print(
            f"Minimum drugs/case : "
            f"{counts.min()}"
        )

        print(
            f"Maximum drugs/case : "
            f"{counts.max()}"
        )

        print(
            f"Average drugs/case : "
            f"{counts.mean():.2f}"
        )

    # --------------------------------------------------------
    # Duplicate drug indexes
    # --------------------------------------------------------

    duplicates = normalized[
        normalized.duplicated(
            subset=[
                "safetyreportid",
                "drug_index"
            ],
            keep=False
        )
    ]

    print()
    print("DUPLICATE DRUG INDEXES")
    print("-" * 70)

    print(
        f"Duplicate records : "
        f"{len(duplicates)}"
    )

    if len(duplicates) == 0:
        print(
            "PASS - No duplicate "
            "case/drug indexes."
        )
    else:
        print(
            "FAIL - Duplicate "
            "case/drug indexes found."
        )

    # --------------------------------------------------------
    # Alignment mismatches
    # --------------------------------------------------------

    mismatch_cases = alignment[
        alignment["mismatched_field_count"] > 0
    ]

    print()
    print("FIELD ALIGNMENT")
    print("-" * 70)

    print(
        f"Cases with field-length mismatch : "
        f"{len(mismatch_cases)}"
    )

    if len(mismatch_cases) == 0:

        print(
            "PASS - All drug fields have "
            "consistent lengths."
        )

    else:

        print(
            "INFO - Some source fields have "
            "different lengths."
        )

        print(
            "These are preserved as missing "
            "values rather than shifting "
            "later drug records."
        )

    # --------------------------------------------------------
    # Null summary
    # --------------------------------------------------------

    print()
    print("NULL SUMMARY")
    print("-" * 70)

    important_fields = [
        "medicinal_product",
        "drug_characterization",
        "active_substance",
        "administration_route",
        "indication",
        "action_taken",
        "dose_text",
        "dosage_form",
    ]

    for field in important_fields:

        if field in normalized.columns:

            missing = normalized[field].isna().sum()

            percentage = (
                missing / len(normalized) * 100
                if len(normalized)
                else 0
            )

            print(
                f"{field:<30} "
                f"{missing:>6} "
                f"({percentage:>6.2f}%)"
            )


# ============================================================
# SAVE OUTPUT
# ============================================================

def save_outputs(
    normalized,
    alignment
):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    normalized.to_csv(
        NORMALIZED_OUTPUT,
        index=False,
        encoding="utf-8-sig"
    )

    alignment.to_csv(
        ALIGNMENT_OUTPUT,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print("=" * 70)
    print("OUTPUT FILES")
    print("=" * 70)

    print(
        f"Normalized dataset : "
        f"{NORMALIZED_OUTPUT}"
    )

    print(
        f"Alignment report   : "
        f"{ALIGNMENT_OUTPUT}"
    )


# ============================================================
# SAMPLE OUTPUT
# ============================================================

def show_samples(normalized):

    print()
    print("=" * 70)
    print("SAMPLE NORMALIZED DRUG RECORDS")
    print("=" * 70)

    sample_cases = (
        normalized["safetyreportid"]
        .drop_duplicates()
        .head(3)
        .tolist()
    )

    for case_id in sample_cases:

        case_df = normalized[
            normalized["safetyreportid"]
            == case_id
        ]

        print()
        print("-" * 70)
        print(
            f"CASE ID: {case_id}"
        )
        print("-" * 70)

        for _, drug in case_df.head(15).iterrows():

            print(
                f"\nDrug {int(drug['drug_index']) + 1}: "
                f"{drug['medicinal_product']}"
            )

            print(
                f"  Characterization : "
                f"{drug['drug_characterization']}"
            )

            print(
                f"  Active substance : "
                f"{drug['active_substance']}"
            )

            print(
                f"  Route            : "
                f"{drug['administration_route']}"
            )

            print(
                f"  Indication       : "
                f"{drug['indication']}"
            )

            print(
                f"  Action taken     : "
                f"{drug['action_taken']}"
            )

            print(
                f"  Dose text        : "
                f"{drug['dose_text']}"
            )

            print(
                f"  Dosage form      : "
                f"{drug['dosage_form']}"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    df = load_dataset()

    validate_schema(df)

    latest = keep_latest_versions(df)

    normalized, alignment = normalize_drugs(
        latest
    )

    validate_normalized_data(
        normalized,
        alignment
    )

    save_outputs(
        normalized,
        alignment
    )

    show_samples(
        normalized
    )

    print()
    print("=" * 70)
    print("DRUG NORMALIZATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()