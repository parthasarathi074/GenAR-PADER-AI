from pathlib import Path

from src.ingestion.loader import load_excel
from src.normalization.versions import (
    select_latest_versions,
)
from src.normalization.drugs import (
    normalize_drugs,
    validate_drug_alignment,
)


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

df = load_excel(DATA_FILE)


# --------------------------------------------------
# Select latest versions
# --------------------------------------------------

latest_df = select_latest_versions(df)


# --------------------------------------------------
# Test cases
# --------------------------------------------------

TARGET_CASES = [
    24780403,
    24780599,
    24780680,
    24784989,
    24787006,
    24787240,
]


print("=" * 80)
print("DRUG NORMALIZATION TEST")
print("=" * 80)


# --------------------------------------------------
# Inspect selected cases
# --------------------------------------------------

for case_id in TARGET_CASES:

    matching = latest_df[
        latest_df["safetyreportid"] == case_id
    ]

    if matching.empty:
        print(
            f"\nCase {case_id} not found."
        )
        continue

    row = matching.iloc[0]

    drugs = normalize_drugs(row)

    validation = validate_drug_alignment(row)

    print("\n" + "-" * 80)

    print(f"CASE ID: {case_id}")

    print(
        f"Drug count: {len(drugs)}"
    )

    print(
        f"Aligned: {validation['aligned']}"
    )

    print("\nDrugs:")

    for index, drug in enumerate(
        drugs,
        start=1,
    ):

        print(
            f"\n  Drug {index}"
        )

        print(
            f"    Product: "
            f"{drug['medicinal_product']}"
        )

        print(
            f"    Active substance: "
            f"{drug['active_substance']}"
        )

        print(
            f"    Characterization: "
            f"{drug['characterization']}"
        )

        print(
            f"    Dose: "
            f"{drug['structured_dose_number']}"
        )

        print(
            f"    Dose unit: "
            f"{drug['structured_dose_unit']}"
        )

        print(
            f"    Route: "
            f"{drug['administration_route']}"
        )

        print(
            f"    Indication: "
            f"{drug['indication']}"
        )

        print(
            f"    Action taken: "
            f"{drug['action_taken']}"
        )


# --------------------------------------------------
# Global alignment validation
# --------------------------------------------------

print("\n" + "=" * 80)
print("GLOBAL DRUG ALIGNMENT VALIDATION")
print("=" * 80)


total_drugs = 0
aligned_cases = 0
misaligned_cases = 0


for _, row in latest_df.iterrows():

    validation = validate_drug_alignment(row)

    drugs = normalize_drugs(row)

    total_drugs += len(drugs)

    if validation["aligned"]:

        aligned_cases += 1

    else:

        misaligned_cases += 1

        print("\nMISALIGNED CASE:")

        print(
            "Case ID:",
            row["safetyreportid"]
        )

        print(
            "Drug count:",
            validation["drug_count"]
        )

        print(
            "Mismatches:",
            validation["mismatches"]
        )


print("\n" + "-" * 80)

print(
    f"Latest cases       : "
    f"{len(latest_df)}"
)

print(
    f"Total drug records : "
    f"{total_drugs}"
)

print(
    f"Aligned cases      : "
    f"{aligned_cases}"
)

print(
    f"Misaligned cases   : "
    f"{misaligned_cases}"
)


print("\n" + "=" * 80)
print("DRUG NORMALIZATION TEST COMPLETE")
print("=" * 80)