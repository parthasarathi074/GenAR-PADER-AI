import os
import ast
import pandas as pd
from collections import Counter

# =============================================================================
# PHASE 5 - PHARMACOVIGILANCE ANALYSIS
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_FILE = os.path.join(DATA_DIR, "integrated_icsr_cases.csv")

CASE_OUTPUT = os.path.join(DATA_DIR, "phase5_case_cohort.csv")
REACTION_OUTPUT = os.path.join(DATA_DIR, "phase5_case_reactions.csv")
SIGNAL_OUTPUT = os.path.join(DATA_DIR, "phase5_signal_candidates.csv")
SUMMARY_OUTPUT = os.path.join(DATA_DIR, "phase5_signal_summary.csv")


print("=" * 100)
print("PHASE 5 - PHARMACOVIGILANCE ANALYSIS")
print("=" * 100)


# =============================================================================
# HELPERS
# =============================================================================

def is_missing(value):
    if pd.isna(value):
        return True

    text = str(value).strip()

    return text == "" or text.lower() in {
        "nan",
        "none",
        "null",
        "na",
        "n/a"
    }


def parse_list(value):
    """
    Parse a normalized record-list field.

    The normalized integrated dataset stores drug/reaction records
    as Python-list-like strings.

    Embedded commas inside a reaction term must remain part of
    the same reaction term.
    """

    if is_missing(value):
        return []

    if isinstance(value, list):
        return value

    text = str(value).strip()

    # Preferred representation: Python list string
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = ast.literal_eval(text)

            if isinstance(parsed, list):
                return [
                    str(x).strip()
                    for x in parsed
                    if not is_missing(x)
                ]

        except Exception:
            pass

    # Fallback only for simple comma-separated values.
    # Do NOT use this on raw ICSR fields.
    return [
        item.strip()
        for item in text.split(",")
        if item.strip()
    ]


def contains_bisoprolol(product_text):
    if is_missing(product_text):
        return False

    text = str(product_text).upper()

    return "BISOPROLOL" in text


# =============================================================================
# FILE CHECK
# =============================================================================

print("\n" + "=" * 100)
print("FILE CHECK")
print("-" * 100)

if not os.path.exists(INPUT_FILE):
    print("FAIL - integrated_icsr_cases.csv not found.")
    raise SystemExit(1)

print("PASS - integrated_icsr_cases.csv")


# =============================================================================
# LOAD DATA
# =============================================================================

print("\n" + "=" * 100)
print("LOADING INTEGRATED DATASET")
print("-" * 100)

df = pd.read_csv(INPUT_FILE)

print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns)}")


# =============================================================================
# REQUIRED COLUMNS
# =============================================================================

required_columns = [
    "safetyreportid",
    "safetyreportversion",
    "primarysourcecountry",
    "occurcountry",
    "reporttype",
    "serious",
    "seriousnessdeath",
    "seriousnesslifethreatening",
    "seriousnesshospitalization",
    "seriousnessdisabling",
    "patient_sex",
    "patient_age",
    "patient_age_unit",
    "drug_count",
    "drug_products",
    "drug_records",
    "reaction_count",
    "reaction_terms",
    "reaction_records",
    "case_integration_status",
]

print("\n" + "=" * 100)
print("COLUMN VALIDATION")
print("-" * 100)

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    print("FAIL - Missing columns:")
    for col in missing:
        print(f"  {col}")
    raise SystemExit(1)

print("PASS - All required analytical columns present.")


# =============================================================================
# CASE-LEVEL VALIDATION
# =============================================================================

print("\n" + "=" * 100)
print("CASE-LEVEL VALIDATION")
print("-" * 100)

duplicate_cases = df["safetyreportid"].duplicated().sum()

if duplicate_cases:
    print(f"FAIL - Duplicate cases: {duplicate_cases}")
    raise SystemExit(1)

print("PASS - One row per safety report.")

if df["safetyreportid"].isna().any():
    print("FAIL - Missing safety report IDs.")
    raise SystemExit(1)

print("PASS - No missing safety report IDs.")


# =============================================================================
# BISOPROLOL COHORT
# =============================================================================

print("\n" + "=" * 100)
print("BISOPROLOL EXPOSURE COHORT")
print("-" * 100)

df["bisoprolol_exposed"] = df["drug_products"].apply(
    contains_bisoprolol
)

bisoprolol_df = df[df["bisoprolol_exposed"]].copy()

print(f"Total integrated cases       : {len(df):,}")
print(f"Bisoprolol-containing cases  : {len(bisoprolol_df):,}")
print(f"Non-Bisoprolol cases         : {len(df) - len(bisoprolol_df):,}")


if len(bisoprolol_df) == 0:
    print("FAIL - No Bisoprolol exposure records detected.")
    raise SystemExit(1)

print("PASS - Bisoprolol cohort detected.")


# =============================================================================
# COMPARATOR AVAILABILITY
# =============================================================================

print("\n" + "=" * 100)
print("COMPARATOR COHORT CHECK")
print("-" * 100)

non_bisoprolol = df[~df["bisoprolol_exposed"]]

if len(non_bisoprolol) == 0:
    print("INFO - No internal non-Bisoprolol comparator cases exist.")
    print("INFO - ROR/PRR will NOT be calculated.")
    print("INFO - Frequency screening only.")
else:
    print(f"Non-Bisoprolol comparator cases : {len(non_bisoprolol):,}")


# =============================================================================
# SAVE CASE COHORT
# =============================================================================

case_columns = [
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
    "seriousnessdisabling",
    "patient_sex",
    "patient_age",
    "patient_age_unit",
    "drug_count",
    "drug_products",
    "reaction_count",
    "reaction_terms",
    "case_integration_status",
    "bisoprolol_exposed",
]

case_cohort = bisoprolol_df[case_columns].copy()

case_cohort.to_csv(
    CASE_OUTPUT,
    index=False,
    encoding="utf-8-sig"
)

print("\nPASS - Case cohort created:")
print(CASE_OUTPUT)


# =============================================================================
# BUILD CASE × REACTION DATASET
# =============================================================================

print("\n" + "=" * 100)
print("BUILDING CASE × REACTION ANALYSIS DATASET")
print("-" * 100)

reaction_rows = []

for _, row in bisoprolol_df.iterrows():

    case_id = row["safetyreportid"]

    reactions = parse_list(row["reaction_terms"])

    for reaction_index, reaction in enumerate(reactions):

        reaction = str(reaction).strip()

        if not reaction:
            continue

        reaction_rows.append({
            "safetyreportid": case_id,
            "reaction_index": reaction_index,
            "reactionmeddrapt": reaction,
            "serious": row["serious"],
            "seriousnessdeath": row["seriousnessdeath"],
            "seriousnesslifethreatening": row[
                "seriousnesslifethreatening"
            ],
            "seriousnesshospitalization": row[
                "seriousnesshospitalization"
            ],
            "seriousnessdisabling": row[
                "seriousnessdisabling"
            ],
            "patient_sex": row["patient_sex"],
            "patient_age": row["patient_age"],
            "patient_age_unit": row["patient_age_unit"],
            "primarysourcecountry": row["primarysourcecountry"],
            "occurcountry": row["occurcountry"],
            "reporttype": row["reporttype"],
        })


reaction_df = pd.DataFrame(reaction_rows)

print(f"Case × reaction rows : {len(reaction_df):,}")
print(f"Unique cases         : {reaction_df['safetyreportid'].nunique():,}")
print(
    f"Unique reactions     : "
    f"{reaction_df['reactionmeddrapt'].nunique():,}"
)

reaction_df.to_csv(
    REACTION_OUTPUT,
    index=False,
    encoding="utf-8-sig"
)

print("PASS - Case × reaction dataset created:")
print(REACTION_OUTPUT)


# =============================================================================
# REACTION FREQUENCY
# =============================================================================

print("\n" + "=" * 100)
print("REACTION FREQUENCY ANALYSIS")
print("-" * 100)

reaction_case_counts = (
    reaction_df
    .groupby("reactionmeddrapt")["safetyreportid"]
    .nunique()
    .reset_index(name="case_count")
)

reaction_case_counts = reaction_case_counts.sort_values(
    ["case_count", "reactionmeddrapt"],
    ascending=[False, True]
).reset_index(drop=True)

total_cases = len(bisoprolol_df)

reaction_case_counts["percentage_of_cases"] = (
    reaction_case_counts["case_count"] /
    total_cases *
    100
).round(2)


# =============================================================================
# SERIOUS CASE FREQUENCY
# =============================================================================

serious_mask = (
    reaction_df["serious"]
    .astype(str)
    .str.strip()
    .str.lower()
    == "serious"
)

serious_reactions = reaction_df[serious_mask]

serious_case_counts = (
    serious_reactions
    .groupby("reactionmeddrapt")["safetyreportid"]
    .nunique()
    .reset_index(name="serious_case_count")
)

reaction_case_counts = reaction_case_counts.merge(
    serious_case_counts,
    on="reactionmeddrapt",
    how="left"
)

reaction_case_counts["serious_case_count"] = (
    reaction_case_counts["serious_case_count"]
    .fillna(0)
    .astype(int)
)


# =============================================================================
# SIGNAL SCREEN
# =============================================================================

print("\n" + "=" * 100)
print("EXPLORATORY SIGNAL-CANDIDATE SCREEN")
print("-" * 100)

# Minimum number of distinct Bisoprolol cases reporting the reaction.
MIN_CASES = 5

signal_df = reaction_case_counts[
    reaction_case_counts["case_count"] >= MIN_CASES
].copy()

signal_df["screening_rule"] = (
    f"At least {MIN_CASES} Bisoprolol-containing cases"
)

signal_df["analysis_type"] = "frequency_screen"

signal_df["causality_established"] = False

signal_df["disproportionality_available"] = False


print(
    f"Candidate reactions (>= {MIN_CASES} cases): "
    f"{len(signal_df):,}"
)

print("\nTOP 30 CANDIDATES")
print("-" * 100)

for _, row in signal_df.head(30).iterrows():

    print(
        f"{int(row['case_count']):5d}  "
        f"{row['percentage_of_cases']:6.2f}%  "
        f"{row['reactionmeddrapt']}"
    )


# =============================================================================
# SAVE SIGNAL DATASET
# =============================================================================

signal_df.to_csv(
    SIGNAL_OUTPUT,
    index=False,
    encoding="utf-8-sig"
)

print("\nPASS - Signal candidate dataset created:")
print(SIGNAL_OUTPUT)


# =============================================================================
# SUMMARY
# =============================================================================

summary_rows = [
    {
        "metric": "total_integrated_cases",
        "value": len(df),
    },
    {
        "metric": "bisoprolol_exposed_cases",
        "value": len(bisoprolol_df),
    },
    {
        "metric": "non_bisoprolol_cases",
        "value": len(non_bisoprolol),
    },
    {
        "metric": "total_case_reaction_records",
        "value": len(reaction_df),
    },
    {
        "metric": "unique_reaction_terms",
        "value": reaction_df["reactionmeddrapt"].nunique(),
    },
    {
        "metric": "signal_candidates_min_5_cases",
        "value": len(signal_df),
    },
    {
        "metric": "comparator_available",
        "value": len(non_bisoprolol) > 0,
    },
    {
        "metric": "disproportionality_analysis_performed",
        "value": False,
    },
]

summary_df = pd.DataFrame(summary_rows)

summary_df.to_csv(
    SUMMARY_OUTPUT,
    index=False,
    encoding="utf-8-sig"
)

print("\nPASS - Phase 5 summary created:")
print(SUMMARY_OUTPUT)


# =============================================================================
# FINAL SAFETY STATEMENT
# =============================================================================

print("\n" + "=" * 100)
print("PHASE 5 ANALYSIS RESULT")
print("=" * 100)

print(f"Integrated cases                 : {len(df):,}")
print(f"Bisoprolol-containing cases      : {len(bisoprolol_df):,}")
print(f"Case × reaction records          : {len(reaction_df):,}")
print(
    f"Unique reaction terms            : "
    f"{reaction_df['reactionmeddrapt'].nunique():,}"
)
print(f"Signal candidates (>=5 cases)    : {len(signal_df):,}")

if len(non_bisoprolol) == 0:
    print("\nCOMPARATOR STATUS")
    print("-" * 100)
    print("No internal non-Bisoprolol comparator is available.")
    print("ROR/PRR has NOT been calculated.")
    print("Frequency screening only.")
else:
    print("\nCOMPARATOR STATUS")
    print("-" * 100)
    print("Internal comparator available.")
    print("Disproportionality analysis can be performed in the next step.")

print("\nIMPORTANT")
print("-" * 100)
print("This analysis is exploratory.")
print("Frequency does not establish causality.")
print("Signal candidates are not confirmed adverse reactions.")
print("No artificial comparator cohort has been created.")

print("\n" + "=" * 100)
print("PHASE 5 ANALYSIS COMPLETE")
print("=" * 100)