import os
import pandas as pd


NORMALIZED_FILE = r"data\normalized_reactions.csv"
REPORT_FILE = r"data\reaction_alignment_report.csv"


print("=" * 100)
print("FINAL REACTION NORMALIZATION QUALITY CHECK")
print("=" * 100)


# ============================================================
# FILE CHECK
# ============================================================

print()
print("FILE CHECK")
print("-" * 100)

if not os.path.exists(NORMALIZED_FILE):
    print("FAIL - normalized_reactions.csv not found.")
    raise SystemExit(1)

if not os.path.exists(REPORT_FILE):
    print("FAIL - reaction_alignment_report.csv not found.")
    raise SystemExit(1)

print("PASS - normalized_reactions.csv")
print("PASS - reaction_alignment_report.csv")


# ============================================================
# LOAD
# ============================================================

df = pd.read_csv(
    NORMALIZED_FILE,
    dtype=str
)

report = pd.read_csv(
    REPORT_FILE,
    dtype=str
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

print()
print("COLUMN VALIDATION")
print("-" * 100)

required_columns = [
    "safetyreportid",
    "safetyreportversion",
    "reaction_index",
    "reactionmeddraversionpt",
    "reactionmeddrapt",
    "reactionoutcome",
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    print(f"FAIL - Missing columns: {missing}")
    raise SystemExit(1)

print("PASS - Required columns present")


# ============================================================
# BASIC DATASET
# ============================================================

print()
print("DATASET")
print("-" * 100)

print(
    f"Normalized reaction rows : {len(df)}"
)

print(
    f"Unique cases             : "
    f"{df['safetyreportid'].nunique()}"
)


# ============================================================
# EMPTY REACTION TERMS
# ============================================================

empty_terms = (
    df["reactionmeddrapt"]
    .fillna("")
    .str.strip()
    .eq("")
)

print()
print("MISSING REACTION TERMS")
print("-" * 100)

print(
    f"Missing reaction terms : "
    f"{empty_terms.sum()}"
)

if empty_terms.sum() == 0:
    print(
        "PASS - Every normalized reaction has a reaction term."
    )
else:
    print(
        "INFO - Some reaction terms are missing."
    )


# ============================================================
# DUPLICATE CASE / INDEX
# ============================================================

duplicates = df.duplicated(
    subset=[
        "safetyreportid",
        "reaction_index",
    ]
)

print()
print("DUPLICATE REACTION INDEXES")
print("-" * 100)

print(
    f"Duplicate records : {duplicates.sum()}"
)

if duplicates.sum() == 0:
    print(
        "PASS - No duplicate case/reaction indexes."
    )
else:
    print(
        "FAIL - Duplicate reaction indexes detected."
    )


# ============================================================
# CONTIGUOUS INDEX CHECK
# ============================================================

print()
print("REACTION INDEX VALIDATION")
print("-" * 100)

index_errors = []

for case_id, group in df.groupby("safetyreportid"):

    indexes = sorted(
        pd.to_numeric(
            group["reaction_index"],
            errors="coerce"
        )
        .dropna()
        .astype(int)
        .tolist()
    )

    expected = list(range(len(indexes)))

    if indexes != expected:

        index_errors.append(case_id)


print(
    f"Cases with non-contiguous indexes : "
    f"{len(index_errors)}"
)

if len(index_errors) == 0:
    print(
        "PASS - Reaction indexes are contiguous from 0."
    )
else:
    print(
        "FAIL - Non-contiguous reaction indexes detected."
    )


# ============================================================
# ALIGNMENT REPORT
# ============================================================

print()
print("ALIGNMENT REPORT")
print("-" * 100)

remaining_warnings = report[
    report["aligned"].astype(str).str.lower()
    != "true"
]

print(
    f"Alignment report rows : "
    f"{len(report)}"
)

print(
    f"Remaining warnings    : "
    f"{len(remaining_warnings)}"
)

if len(remaining_warnings) == 0:

    print(
        "PASS - All cases are aligned."
    )

else:

    print(
        "FAIL - Alignment warnings remain."
    )

    print(
        remaining_warnings.to_string(
            index=False
        )
    )


# ============================================================
# COMMA TERM CHECK
# ============================================================

print()
print("EMBEDDED-COMMA TERM CHECK")
print("-" * 100)

comma_reactions = df[
    df["reactionmeddrapt"]
    .fillna("")
    .str.contains(",", regex=False)
]

print(
    f"Reactions containing commas : "
    f"{len(comma_reactions)}"
)

if len(comma_reactions) > 0:

    print()
    print("Examples:")

    for term in sorted(
        comma_reactions[
            "reactionmeddrapt"
        ].unique()
    ):

        print(
            f"  {term}"
        )


# ============================================================
# KNOWN CASE VALIDATION
# ============================================================

print()
print("KNOWN PHASE 2 MISMATCH VALIDATION")
print("-" * 100)

expected_terms = {
    "25187835": [
        "Hallucination, auditory"
    ],
    "25282743": [
        "Hallucination, visual"
    ],
    "25459724": [
        "Hallucinations, mixed"
    ],
    "25517207": [
        "Hallucination, visual"
    ],
    "26115793": [
        "Hallucination, visual"
    ],
    "26144528": [
        "Hallucination, visual"
    ],
}

known_failures = []

for case_id, terms in expected_terms.items():

    case_terms = set(
        df[
            df["safetyreportid"] == case_id
        ]["reactionmeddrapt"]
        .dropna()
        .tolist()
    )

    for term in terms:

        if term not in case_terms:

            known_failures.append(
                (case_id, term)
            )


if not known_failures:

    print(
        "PASS - All known embedded-comma terms "
        "were preserved."
    )

else:

    print(
        "FAIL - Some known comma terms were not preserved."
    )

    for case_id, term in known_failures:

        print(
            f"  {case_id}: {term}"
        )


# ============================================================
# FINAL RESULT
# ============================================================

print()
print("=" * 100)

if (
    len(remaining_warnings) == 0
    and duplicates.sum() == 0
    and len(index_errors) == 0
    and not known_failures
):

    print("FINAL RESULT: PASS")
    print()
    print(
        "Reaction normalization Phase 2 is COMPLETE."
    )
    print(
        "The dataset is ready for Phase 3."
    )

else:

    print("FINAL RESULT: REVIEW REQUIRED")
    print()
    print(
        "Do NOT proceed to Phase 3 until the "
        "remaining validation issues are resolved."
    )

print("=" * 100)