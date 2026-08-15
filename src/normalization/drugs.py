import pandas as pd


# --------------------------------------------------
# Drug columns
# --------------------------------------------------

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


def split_drug_field(value):
    """
    Split a multi-valued drug field.

    Important:
    - Comma separates drug records.
    - Backslash is preserved because it can occur
      inside combination-product names.
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


def normalize_drugs(row):
    """
    Convert one raw case row into normalized drug records.

    Drug fields are positionally aligned.

    Example:

        product[0]
        active_substance[0]
        characterization[0]

    belong to the same drug.
    """

    field_values = {}

    for name, column in DRUG_COLUMNS.items():

        field_values[name] = split_drug_field(
            row[column]
        )

    # --------------------------------------------------
    # Determine number of drug records
    # --------------------------------------------------

    drug_count = max(
        (
            len(values)
            for values in field_values.values()
        ),
        default=0,
    )

    normalized = []

    # --------------------------------------------------
    # Build each drug record
    # --------------------------------------------------

    for index in range(drug_count):

        drug = {}

        for field_name, values in field_values.items():

            if index < len(values):

                drug[field_name] = values[index]

            else:

                drug[field_name] = None

        normalized.append(drug)

    return normalized


def validate_drug_alignment(row):
    """
    Check whether all populated multi-valued drug
    fields have the same number of values.

    Returns diagnostic information rather than
    silently modifying data.
    """

    field_counts = {}

    for name, column in DRUG_COLUMNS.items():

        values = split_drug_field(
            row[column]
        )

        field_counts[name] = len(values)

    non_zero_counts = [
        count
        for count in field_counts.values()
        if count > 0
    ]

    if not non_zero_counts:

        return {
            "aligned": True,
            "drug_count": 0,
            "field_counts": field_counts,
        }

    expected_count = max(non_zero_counts)

    mismatches = {
        field: count
        for field, count in field_counts.items()
        if count not in (0, expected_count)
    }

    return {
        "aligned": len(mismatches) == 0,
        "drug_count": expected_count,
        "field_counts": field_counts,
        "mismatches": mismatches,
    }