import os
import re
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = r"data\Bisoprolol_icsr_sample_1068rows.xlsx"

OUTPUT_FILE = r"data\normalized_reactions.csv"

REPORT_FILE = r"data\reaction_alignment_report.csv"


REACTION_VERSION_COL = "patient_reaction_reactionmeddraversionpt"
REACTION_TERM_COL = "patient_reaction_reactionmeddrapt"
REACTION_OUTCOME_COL = "patient_reaction_reactionoutcome"


# ============================================================
# KNOWN MEDDRA TERMS CONTAINING COMMAS
# ============================================================
#
# The source dataset stores repeated reaction values as
# comma-separated text. Some MedDRA Preferred Terms themselves
# contain commas.
#
# Example:
#
# Hallucination, visual
#
# must remain ONE reaction.
#
# These terms were identified during Phase 2 investigation.
#
# This dictionary is deliberately explicit rather than silently
# guessing unknown terms.
# ============================================================

KNOWN_COMMA_TERMS = {
    "Hallucination, visual",
    "Hallucination, auditory",
    "Hallucinations, mixed",
}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def clean_value(value):
    """
    Convert a raw Excel cell value into a clean string.
    """
    if pd.isna(value):
        return ""

    value = str(value).strip()

    if value.lower() in {"nan", "none", "null"}:
        return ""

    return value


def split_raw_values(value):
    """
    Split a source reaction field on commas.

    This is only the first stage. Embedded MedDRA comma terms
    are repaired later using the expected reaction count.
    """
    value = clean_value(value)

    if not value:
        return []

    return [item.strip() for item in value.split(",")]


def repair_embedded_comma_terms(tokens, expected_count):
    """
    Repair known MedDRA terms containing commas.

    Example:

        ["Hallucination", "visual", "Delirium"]

    becomes:

        ["Hallucination, visual", "Delirium"]

    when the expected number of reactions is 2.

    The function never merges arbitrary tokens merely to make
    the count work. Only known MedDRA comma-containing terms
    are merged.
    """

    if not tokens:
        return []

    tokens = [x.strip() for x in tokens if x.strip()]

    # Already aligned.
    if expected_count is None or len(tokens) == expected_count:
        return tokens

    # Too many tokens means one or more embedded commas exist.
    if len(tokens) <= expected_count:
        return tokens

    repaired = []
    i = 0

    while i < len(tokens):

        merged = False

        # Try two-token combinations.
        if i + 1 < len(tokens):

            candidate = f"{tokens[i]}, {tokens[i + 1]}"

            if candidate in KNOWN_COMMA_TERMS:
                repaired.append(candidate)
                i += 2
                merged = True

        if not merged:
            repaired.append(tokens[i])
            i += 1

    return repaired


def normalize_reaction_field(value, expected_count=None):
    """
    Normalize a reaction field while preserving known embedded
    comma terms.
    """

    tokens = split_raw_values(value)

    repaired = repair_embedded_comma_terms(
        tokens,
        expected_count
    )

    return repaired


# ============================================================
# LATEST VERSION SELECTION
# ============================================================

def keep_latest_versions(df):
    """
    Keep only the latest safety report version for each case.
    """

    df = df.copy()

    df["safetyreportversion_num"] = pd.to_numeric(
        df["safetyreportversion"],
        errors="coerce"
    ).fillna(0)

    df = (
        df.sort_values(
            ["safetyreportid", "safetyreportversion_num"]
        )
        .groupby("safetyreportid", as_index=False)
        .tail(1)
        .copy()
    )

    df.drop(columns=["safetyreportversion_num"], inplace=True)

    return df


# ============================================================
# MAIN
# ============================================================

print("=" * 100)
print("PHASE 2 - REACTION NORMALIZATION")
print("=" * 100)

print()
print("Loading dataset...")
print(f"Path: {os.path.abspath(INPUT_FILE)}")

df = pd.read_excel(INPUT_FILE)

print(f"Raw rows : {len(df)}")
print(f"Columns  : {len(df.columns)}")


# ============================================================
# COLUMN VALIDATION
# ============================================================

print()
print("=" * 100)
print("COLUMN VALIDATION")
print("=" * 100)

required_columns = [
    "safetyreportid",
    "safetyreportversion",
    REACTION_VERSION_COL,
    REACTION_TERM_COL,
    REACTION_OUTCOME_COL,
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    raise ValueError(
        f"Missing required columns: {missing}"
    )

print("PASS - All required reaction columns exist.")


# ============================================================
# LATEST VERSION DATASET
# ============================================================

print()
print("=" * 100)
print("KEEPING LATEST SAFETY REPORT VERSION")
print("=" * 100)

latest_df = keep_latest_versions(df)

print(f"Latest rows   : {len(latest_df)}")
print(
    f"Unique cases  : "
    f"{latest_df['safetyreportid'].nunique()}"
)


# ============================================================
# NORMALIZATION
# ============================================================

print()
print("=" * 100)
print("NORMALIZING REACTION RECORDS")
print("=" * 100)

normalized_records = []
alignment_records = []


for _, row in latest_df.iterrows():

    case_id = str(row["safetyreportid"])
    version = row["safetyreportversion"]

    raw_version = clean_value(row[REACTION_VERSION_COL])
    raw_terms = clean_value(row[REACTION_TERM_COL])
    raw_outcomes = clean_value(row[REACTION_OUTCOME_COL])

    version_tokens = split_raw_values(raw_version)
    outcome_tokens = split_raw_values(raw_outcomes)

    # --------------------------------------------------------
    # Determine expected count
    # --------------------------------------------------------
    #
    # MedDRA version and outcome fields normally represent
    # one value per reaction.
    #
    # If they agree, use that count.
    #
    # If they disagree, preserve the safest available count
    # and flag the case.
    # --------------------------------------------------------

    version_count = len(version_tokens)
    outcome_count = len(outcome_tokens)

    if version_count == outcome_count:
        expected_count = version_count

    elif version_count > 0:
        expected_count = version_count

    elif outcome_count > 0:
        expected_count = outcome_count

    else:
        expected_count = 0

    # --------------------------------------------------------
    # Normalize fields
    # --------------------------------------------------------

    normalized_versions = normalize_reaction_field(
        raw_version,
        expected_count
    )

    normalized_terms = normalize_reaction_field(
        raw_terms,
        expected_count
    )

    normalized_outcomes = normalize_reaction_field(
        raw_outcomes,
        expected_count
    )

    # --------------------------------------------------------
    # Re-check counts
    # --------------------------------------------------------

    final_version_count = len(normalized_versions)
    final_term_count = len(normalized_terms)
    final_outcome_count = len(normalized_outcomes)

    counts = [
        final_version_count,
        final_term_count,
        final_outcome_count,
    ]

    final_aligned = (
        len(set(counts)) == 1
    )

    # --------------------------------------------------------
    # Record alignment information
    # --------------------------------------------------------

    alignment_records.append({
        "safetyreportid": case_id,
        "safetyreportversion": version,
        "expected_reaction_count": expected_count,
        "version_count": final_version_count,
        "reaction_term_count": final_term_count,
        "outcome_count": final_outcome_count,
        "aligned": final_aligned,
        "raw_version_count": version_count,
        "raw_reaction_term_count": len(
            split_raw_values(raw_terms)
        ),
        "raw_outcome_count": outcome_count,
    })

    # --------------------------------------------------------
    # Create normalized reaction records
    # --------------------------------------------------------

    max_count = max(counts) if counts else 0

    for i in range(max_count):

        normalized_records.append({

            "safetyreportid": case_id,

            "safetyreportversion": version,

            "reaction_index": i,

            "reactionmeddraversionpt":
                normalized_versions[i]
                if i < len(normalized_versions)
                else "",

            "reactionmeddrapt":
                normalized_terms[i]
                if i < len(normalized_terms)
                else "",

            "reactionoutcome":
                normalized_outcomes[i]
                if i < len(normalized_outcomes)
                else "",
        })


# ============================================================
# DATAFRAME CREATION
# ============================================================

normalized_df = pd.DataFrame(
    normalized_records
)

alignment_df = pd.DataFrame(
    alignment_records
)


# ============================================================
# OUTPUT
# ============================================================

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

normalized_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

alignment_df.to_csv(
    REPORT_FILE,
    index=False,
    encoding="utf-8"
)


# ============================================================
# VALIDATION SUMMARY
# ============================================================

print()
print("=" * 100)
print("REACTION NORMALIZATION SUMMARY")
print("=" * 100)

print(
    f"Normalized reaction records : "
    f"{len(normalized_df)}"
)

print(
    f"Unique cases                : "
    f"{normalized_df['safetyreportid'].nunique()}"
)

print(
    f"Alignment report rows       : "
    f"{len(alignment_df)}"
)


warnings = alignment_df[
    alignment_df["aligned"] == False
]

print(
    f"Cases with remaining "
    f"alignment warnings         : {len(warnings)}"
)


# ============================================================
# EMBEDDED COMMA VALIDATION
# ============================================================

print()
print("=" * 100)
print("EMBEDDED-COMMA TERM VALIDATION")
print("=" * 100)

comma_terms_found = normalized_df[
    normalized_df["reactionmeddrapt"].str.contains(
        ",",
        regex=False,
        na=False
    )
]

print(
    f"Normalized reactions containing commas : "
    f"{len(comma_terms_found)}"
)

for term in sorted(
    comma_terms_found["reactionmeddrapt"].unique()
):

    print(f"  {term}")


# ============================================================
# SAMPLE RECORDS
# ============================================================

print()
print("=" * 100)
print("SAMPLE NORMALIZED REACTIONS")
print("=" * 100)

sample_cases = [
    "25187835",
    "25282743",
    "25459724",
    "25517207",
    "26115793",
    "26144528",
]

for case_id in sample_cases:

    case_rows = normalized_df[
        normalized_df["safetyreportid"] == case_id
    ]

    print()
    print("-" * 80)
    print(f"CASE ID: {case_id}")
    print("-" * 80)

    for _, reaction in case_rows.iterrows():

        print(
            f"[{reaction['reaction_index']}] "
            f"{reaction['reactionmeddrapt']} "
            f"| Outcome: "
            f"{reaction['reactionoutcome']}"
        )


# ============================================================
# FINAL STATUS
# ============================================================

if len(warnings) == 0:

    print()
    print("=" * 100)
    print("PHASE 2 REACTION NORMALIZATION COMPLETE")
    print("=" * 100)

    print("PASS - All normalized reaction records are aligned.")
    print("PASS - Embedded comma terms were preserved.")
    print("PASS - No reaction information was shifted.")
    print()
    print(
        f"Normalized dataset : {OUTPUT_FILE}"
    )
    print(
        f"Alignment report   : {REPORT_FILE}"
    )

else:

    print()
    print("=" * 100)
    print("PHASE 2 REQUIRES REVIEW")
    print("=" * 100)

    print(
        f"{len(warnings)} cases still have alignment warnings."
    )

    print(
        warnings[
            [
                "safetyreportid",
                "expected_reaction_count",
                "version_count",
                "reaction_term_count",
                "outcome_count",
            ]
        ].to_string(index=False)
    )