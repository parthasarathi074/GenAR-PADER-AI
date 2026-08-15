from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

NORM = DATA / "normalized_drugs.csv"
RAW = DATA / "Bisoprolol_icsr_sample_1068rows.xlsx"
REPORT = DATA / "drug_alignment_report.csv"

REQUIRED = [
    "safetyreportid",
    "safetyreportversion",
    "drug_index",
    "drug_count",
    "drug_characterization",
    "medicinal_product",
    "active_substance",
    "administration_route",
    "indication",
    "action_taken",
]


def main():

    print("=" * 70)
    print("FINAL DRUG NORMALIZATION QUALITY CHECK")
    print("=" * 70)

    ok = True

    # ---------------------------------------------------------
    # FILE CHECK
    # ---------------------------------------------------------
    print("\nFILE CHECK")
    print("-" * 70)

    for file in [NORM, RAW, REPORT]:
        if file.exists():
            print(f"PASS - {file.name}")
        else:
            print(f"FAIL - Missing {file}")
            ok = False

    if not ok:
        return 1

    # ---------------------------------------------------------
    # LOAD FILES
    # ---------------------------------------------------------
    df = pd.read_csv(NORM)
    raw = pd.read_excel(RAW, engine="openpyxl")
    report = pd.read_csv(REPORT)

    print("\nDATASET")
    print("-" * 70)
    print(f"Normalized drug rows : {len(df)}")
    print(f"Raw rows             : {len(raw)}")

    # ---------------------------------------------------------
    # REQUIRED COLUMNS
    # ---------------------------------------------------------
    missing_columns = [
        column for column in REQUIRED
        if column not in df.columns
    ]

    if missing_columns:
        print(
            "FAIL - Missing required columns:",
            ", ".join(missing_columns)
        )
        ok = False
    else:
        print("PASS - Required columns present")

    # ---------------------------------------------------------
    # MEDICINAL PRODUCT
    # ---------------------------------------------------------
    product_missing = (
        df["medicinal_product"].isna()
        |
        (
            df["medicinal_product"]
            .astype(str)
            .str.strip()
            .eq("")
        )
    ).sum()

    if product_missing:
        print(
            f"FAIL - Empty medicinal products: "
            f"{product_missing}"
        )
        ok = False
    else:
        print("PASS - No empty medicinal products")

    # ---------------------------------------------------------
    # DUPLICATES
    # ---------------------------------------------------------
    duplicates = df.duplicated(
        ["safetyreportid", "drug_index"]
    ).sum()

    if duplicates:
        print(
            f"FAIL - Duplicate case/drug indexes: "
            f"{duplicates}"
        )
        ok = False
    else:
        print("PASS - No duplicate case/drug indexes")

    # ---------------------------------------------------------
    # DRUG INDEX VALIDATION
    # ---------------------------------------------------------
    bad_indexes = 0
    bad_counts = 0

    for case_id, group in df.groupby(
        "safetyreportid",
        sort=False
    ):

        indexes = sorted(
            pd.to_numeric(
                group["drug_index"],
                errors="coerce"
            )
            .dropna()
            .astype(int)
            .tolist()
        )

        expected_indexes = list(range(len(group)))

        if indexes != expected_indexes:
            bad_indexes += 1

        counts = pd.to_numeric(
            group["drug_count"],
            errors="coerce"
        ).dropna().unique()

        if len(counts) != 1:
            bad_counts += 1
        elif int(counts[0]) != len(group):
            bad_counts += 1

    if bad_indexes:
        print(
            f"FAIL - Cases with invalid drug indexes: "
            f"{bad_indexes}"
        )
        ok = False
    else:
        print(
            "PASS - Drug indexes are contiguous "
            "from 0 for every case"
        )

    if bad_counts:
        print(
            f"FAIL - Cases with incorrect drug_count: "
            f"{bad_counts}"
        )
        ok = False
    else:
        print(
            "PASS - drug_count matches actual records"
        )

    # ---------------------------------------------------------
    # UNIQUE CASES
    # ---------------------------------------------------------
    unique_cases = df["safetyreportid"].nunique()

    print(f"\nUnique cases : {unique_cases}")

    if unique_cases != 1024:
        print(
            f"FAIL - Expected 1024 cases, "
            f"found {unique_cases}"
        )
        ok = False
    else:
        print("PASS - 1,024 unique cases")

    # ---------------------------------------------------------
    # LATEST VERSION VALIDATION
    # ---------------------------------------------------------
    raw["safetyreportid"] = pd.to_numeric(
        raw["safetyreportid"],
        errors="coerce"
    )

    raw["safetyreportversion"] = pd.to_numeric(
        raw["safetyreportversion"],
        errors="coerce"
    )

    latest = (
        raw
        .sort_values(
            ["safetyreportid", "safetyreportversion"]
        )
        .drop_duplicates(
            "safetyreportid",
            keep="last"
        )
    )

    latest_versions = latest.set_index(
        "safetyreportid"
    )["safetyreportversion"]

    normalized_versions = (
        df.groupby("safetyreportid")
        ["safetyreportversion"]
        .first()
    )

    common_cases = (
        latest_versions.index
        .intersection(normalized_versions.index)
    )

    mismatches = (
        latest_versions.loc[common_cases]
        .astype(float)
        .values
        !=
        normalized_versions.loc[common_cases]
        .astype(float)
        .values
    ).sum()

    missing_cases = len(
        latest_versions.index
        .difference(normalized_versions.index)
    )

    extra_cases = len(
        normalized_versions.index
        .difference(latest_versions.index)
    )

    if mismatches or missing_cases or extra_cases:

        print(
            "FAIL - Latest-version validation:"
        )

        print(
            f"  Version mismatches : {mismatches}"
        )

        print(
            f"  Missing cases      : {missing_cases}"
        )

        print(
            f"  Extra cases        : {extra_cases}"
        )

        ok = False

    else:
        print(
            "PASS - Latest safety-report versions retained"
        )

    # ---------------------------------------------------------
    # ALIGNMENT REPORT
    # ---------------------------------------------------------
    report_cases = (
        report["case_id"].nunique()
        if "case_id" in report.columns
        else 0
    )

    print("\nALIGNMENT REPORT")
    print("-" * 70)

    print(
        f"Alignment report rows : {len(report)}"
    )

    print(
        f"Cases with alignment warnings : "
        f"{report_cases}"
    )

    print(
        "INFO - Alignment warnings represent "
        "irregularities in the original source data."
    )

    print(
        "INFO - They are preserved rather than "
        "causing incorrect drug-field shifting."
    )

    # ---------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------
    print("\n" + "=" * 70)

    if ok:

        print("FINAL RESULT: PASS")
        print()
        print(
            "Drug normalization Phase 1 is COMPLETE."
        )
        print(
            "The dataset is ready for Reaction Normalization."
        )

        return 0

    else:

        print("FINAL RESULT: FAIL")
        print()
        print(
            "Fix the failed checks before moving forward."
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())