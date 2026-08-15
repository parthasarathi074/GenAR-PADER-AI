import pandas as pd
import re
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

DATASET = Path("data/Bisoprolol_icsr_sample_1068rows.xlsx")

REACTION_COLUMNS = [
    "patient_reaction_reactionmeddraversionpt",
    "patient_reaction_reactionmeddrapt",
    "patient_reaction_reactionoutcome",
]

MISMATCH_CASES = [
    25187835,
    25282743,
    25459724,
    25517207,
    26115793,
    26144528,
]


# ============================================================
# HELPERS
# ============================================================

def clean_value(value):
    if pd.isna(value):
        return ""

    value = str(value).strip()

    if value.lower() in {"nan", "none", "null"}:
        return ""

    return value


def split_raw_value(value):
    """
    Initial diagnostic splitter.

    IMPORTANT:
    This is only for investigation.
    It is NOT yet the final reaction parser.
    """

    value = clean_value(value)

    if not value:
        return []

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def print_field(name, value):
    values = split_raw_value(value)

    print()
    print(name)
    print("-" * 80)
    print(f"Raw value:")
    print(value)
    print()
    print(f"Naive comma-split count: {len(values)}")

    for i, item in enumerate(values):
        print(f"  [{i}] {item}")


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 100)
print("PHASE 2 - REACTION MISMATCH DEEP INVESTIGATION")
print("=" * 100)

print()
print("Loading dataset...")
print(f"Path: {DATASET}")

df = pd.read_excel(
    DATASET,
    engine="openpyxl"
)

print(f"Raw rows : {len(df)}")
print(f"Columns  : {len(df.columns)}")


# ============================================================
# CHECK COLUMNS
# ============================================================

print()
print("=" * 100)
print("COLUMN VALIDATION")
print("=" * 100)

for column in REACTION_COLUMNS:
    if column not in df.columns:
        raise ValueError(f"Missing required column: {column}")

print("PASS - All reaction columns exist.")


# ============================================================
# KEEP LATEST VERSION
# ============================================================

print()
print("=" * 100)
print("KEEPING LATEST SAFETY REPORT VERSION")
print("=" * 100)

work = df.copy()

work["safetyreportid"] = pd.to_numeric(
    work["safetyreportid"],
    errors="coerce"
)

work["safetyreportversion"] = pd.to_numeric(
    work["safetyreportversion"],
    errors="coerce"
)

work = work.dropna(
    subset=["safetyreportid", "safetyreportversion"]
)

latest = (
    work.sort_values(
        ["safetyreportid", "safetyreportversion"]
    )
    .groupby("safetyreportid", as_index=False)
    .tail(1)
    .copy()
)

print(f"Latest rows   : {len(latest)}")
print(
    f"Unique cases  : "
    f"{latest['safetyreportid'].nunique()}"
)


# ============================================================
# INVESTIGATE SIX MISMATCH CASES
# ============================================================

print()
print("=" * 100)
print("INVESTIGATING KNOWN MISMATCH CASES")
print("=" * 100)


for case_id in MISMATCH_CASES:

    rows = latest[
        latest["safetyreportid"] == case_id
    ]

    print()
    print("=" * 100)

    if rows.empty:
        print(f"CASE ID {case_id} NOT FOUND")
        continue

    row = rows.iloc[0]

    print(f"CASE ID: {case_id}")
    print(f"SAFETY VERSION: {row['safetyreportversion']}")

    print("=" * 100)

    # --------------------------------------------------------
    # BASIC CASE INFORMATION
    # --------------------------------------------------------

    print()
    print("CASE INFORMATION")
    print("-" * 100)

    basic_columns = [
        "safetyreportid",
        "safetyreportversion",
        "receivedate",
        "report_date",
        "transmissiondate",
        "primarysourcecountry",
        "occurcountry",
        "reporttype",
        "serious",
        "patient_patientsex",
        "patient_patientonsetage",
        "patient_patientonsetageunit",
    ]

    for column in basic_columns:

        if column in row.index:
            print(
                f"{column:<45}: "
                f"{clean_value(row[column])}"
            )

    # --------------------------------------------------------
    # REACTION FIELDS
    # --------------------------------------------------------

    print()
    print("REACTION FIELDS")
    print("-" * 100)

    counts = {}

    for column in REACTION_COLUMNS:

        values = split_raw_value(row[column])

        counts[column] = len(values)

        print_field(
            column,
            row[column]
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()
    print("REACTION COUNT SUMMARY")
    print("-" * 100)

    for column, count in counts.items():
        print(
            f"{column:<55}: {count}"
        )

    unique_counts = set(counts.values())

    print()

    if len(unique_counts) == 1:
        print("ALIGNMENT STATUS: OK")
    else:
        print("ALIGNMENT STATUS: WARNING")
        print(
            "The raw comma-separated fields do not "
            "produce equal counts."
        )

    # --------------------------------------------------------
    # SPECIAL CHARACTER CHECK
    # --------------------------------------------------------

    print()
    print("POSSIBLE EMBEDDED-COMMA TERMS")
    print("-" * 100)

    pt_values = split_raw_value(
        row["patient_reaction_reactionmeddrapt"]
    )

    for i, value in enumerate(pt_values):

        if "," in value:
            print(
                f"[{i}] POSSIBLE EMBEDDED COMMA: {value}"
            )

        if len(value.split()) == 1:
            continue

        # Print suspicious terms containing punctuation.
        if re.search(r"[,:;()/]", value):
            print(
                f"[{i}] Punctuation detected: {value}"
            )


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 100)
print("REACTION MISMATCH DEEP INVESTIGATION COMPLETE")
print("=" * 100)