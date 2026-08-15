import pandas as pd
from pathlib import Path
from collections import defaultdict

# ============================================================
# PHASE 3 - REMAINING ICSR STRUCTURE INVESTIGATION
# ============================================================

print("=" * 100)
print("PHASE 3 - REMAINING ICSR STRUCTURE INVESTIGATION")
print("=" * 100)

DATA_PATH = Path("data/Bisoprolol_icsr_sample_1068rows.xlsx")

if not DATA_PATH.exists():
    print(f"ERROR - Dataset not found: {DATA_PATH}")
    raise SystemExit(1)

print("\nLoading dataset...")
print(f"Path: {DATA_PATH.resolve()}")

df = pd.read_excel(DATA_PATH, dtype=str)

print(f"Raw rows : {len(df)}")
print(f"Columns  : {len(df.columns)}")


# ============================================================
# BASIC COLUMN INVENTORY
# ============================================================

print("\n" + "=" * 100)
print("COLUMN INVENTORY")
print("=" * 100)

for i, column in enumerate(df.columns, start=1):
    print(f"{i:02d}. {column}")


# ============================================================
# KEEP LATEST SAFETY REPORT VERSION
# ============================================================

print("\n" + "=" * 100)
print("KEEPING LATEST SAFETY REPORT VERSION")
print("=" * 100)

required = ["safetyreportid", "safetyreportversion"]

missing = [c for c in required if c not in df.columns]

if missing:
    print("ERROR - Missing required columns:")
    for c in missing:
        print(f"  {c}")
    raise SystemExit(1)

df["safetyreportversion_num"] = pd.to_numeric(
    df["safetyreportversion"],
    errors="coerce"
)

latest = (
    df.sort_values(
        ["safetyreportid", "safetyreportversion_num"]
    )
    .groupby("safetyreportid", as_index=False)
    .tail(1)
    .copy()
)

print(f"Latest rows   : {len(latest)}")
print(f"Unique cases  : {latest['safetyreportid'].nunique()}")


# ============================================================
# ALREADY NORMALIZED STRUCTURES
# ============================================================

already_handled = {
    "drug",
    "reaction",
    "patient_drug",
    "patient_reaction",
}


# ============================================================
# IDENTIFY POTENTIAL REPEATING / STRUCTURED FIELDS
# ============================================================

print("\n" + "=" * 100)
print("POTENTIAL PHASE 3 STRUCTURES")
print("=" * 100)

candidate_columns = []

for column in df.columns:

    column_lower = column.lower()

    # Ignore technical/version fields
    if column in required or column == "safetyreportversion_num":
        continue

    # Ignore fields already handled by Phase 1 / Phase 2
    if any(token in column_lower for token in already_handled):
        continue

    # Count non-empty values
    non_empty = latest[column].dropna().astype(str)
    non_empty = non_empty[non_empty.str.strip() != ""]

    if len(non_empty) == 0:
        continue

    comma_rows = non_empty[
        non_empty.str.contains(",", regex=False)
    ]

    candidate_columns.append(
        (
            column,
            len(non_empty),
            len(comma_rows),
            round(len(comma_rows) / len(non_empty) * 100, 2),
        )
    )

print(
    f"{'COLUMN':55} "
    f"{'VALUES':>8} "
    f"{'COMMA ROWS':>12} "
    f"{'COMMA %':>10}"
)

print("-" * 100)

for column, values, comma_rows, percentage in candidate_columns:
    print(
        f"{column:55} "
        f"{values:8} "
        f"{comma_rows:12} "
        f"{percentage:9.2f}%"
    )


# ============================================================
# GROUP COLUMNS BY ICSR STRUCTURE
# ============================================================

print("\n" + "=" * 100)
print("STRUCTURE GROUPING")
print("=" * 100)

groups = defaultdict(list)

for column in df.columns:

    column_lower = column.lower()

    if column == "safetyreportversion_num":
        continue

    if "medicalhistory" in column_lower:
        groups["MEDICAL HISTORY"].append(column)

    elif "pastdrugtherapy" in column_lower:
        groups["PAST DRUG THERAPY"].append(column)

    elif "labtest" in column_lower:
        groups["LAB TESTS"].append(column)

    elif "test" in column_lower:
        groups["TEST / INVESTIGATION"].append(column)

    elif "patient" in column_lower:
        groups["PATIENT INFORMATION"].append(column)

    elif "primarysource" in column_lower:
        groups["PRIMARY SOURCE"].append(column)

    elif "sender" in column_lower:
        groups["SENDER INFORMATION"].append(column)

    elif "receiver" in column_lower:
        groups["RECEIVER INFORMATION"].append(column)

    elif "reportduplicate" in column_lower:
        groups["REPORT DUPLICATE"].append(column)

    elif "summary" in column_lower:
        groups["SUMMARY"].append(column)

    elif "narrative" in column_lower:
        groups["NARRATIVE"].append(column)

    else:
        groups["OTHER"].append(column)


for group_name, columns in groups.items():

    print("\n" + "-" * 100)
    print(group_name)
    print("-" * 100)

    for column in columns:
        print(f"  {column}")


# ============================================================
# DETAILED INVESTIGATION OF REPEATABLE STRUCTURES
# ============================================================

print("\n" + "=" * 100)
print("DETAILED REPEATABLE-STRUCTURE INVESTIGATION")
print("=" * 100)

repeatable_keywords = [
    "medicalhistory",
    "pastdrugtherapy",
    "labtest",
    "test",
    "patient_medical",
    "patient_past",
]

repeatable_columns = []

for column in df.columns:

    column_lower = column.lower()

    if any(keyword in column_lower for keyword in repeatable_keywords):
        repeatable_columns.append(column)


if not repeatable_columns:

    print("No obvious repeatable Phase 3 structure detected.")

else:

    for column in repeatable_columns:

        print("\n" + "=" * 100)
        print(f"COLUMN: {column}")
        print("=" * 100)

        values = latest[column].dropna().astype(str)
        values = values[values.str.strip() != ""]

        print(f"Cases with values : {len(values)}")

        if len(values) > 0:

            counts = values.apply(
                lambda x: len(
                    [v.strip() for v in x.split(",") if v.strip()]
                )
            )

            print(f"Minimum count     : {counts.min()}")
            print(f"Maximum count     : {counts.max()}")
            print(f"Average count     : {counts.mean():.2f}")

            comma_values = values[
                values.str.contains(",", regex=False)
            ]

            print(f"Comma-containing  : {len(comma_values)}")

            print("\nSample raw values:")

            for value in values.head(5):
                print(f"  {value}")


# ============================================================
# SAMPLE CASE INSPECTION
# ============================================================

print("\n" + "=" * 100)
print("REPRESENTATIVE CASE")
print("=" * 100)

if len(latest) > 0:

    sample_case = latest.iloc[0]

    case_id = sample_case["safetyreportid"]

    print(f"CASE ID: {case_id}")
    print(f"SAFETY VERSION: {sample_case['safetyreportversion']}")

    print("\nNon-empty structured fields:")

    for column in df.columns:

        if column == "safetyreportversion_num":
            continue

        value = sample_case[column]

        if pd.notna(value) and str(value).strip() != "":
            print(f"\n{column}")
            print("-" * 80)
            print(str(value))


# ============================================================
# RECOMMENDATION
# ============================================================

print("\n" + "=" * 100)
print("PHASE 3 INVESTIGATION RESULT")
print("=" * 100)

print("""
Phase 1 : Drug normalization       COMPLETE
Phase 2 : Reaction normalization   COMPLETE

Phase 3 : Structure investigation  COMPLETE

The output above identifies the remaining structured ICSR
fields and their cardinality.

IMPORTANT:
Do not normalize a structure merely because it contains commas.
The investigation output must be used to determine whether
commas represent multiple records or are part of a single value.

Next step:
Select the actual repeatable Phase 3 structure from the
investigation results, then create its dedicated normalization
script and validation script.
""")

print("=" * 100)
print("PHASE 3 STRUCTURE INVESTIGATION COMPLETE")
print("=" * 100)