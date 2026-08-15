import os
import pandas as pd

# =============================================================================
# PHASE 5 - PHARMACOVIGILANCE ANALYSIS VALIDATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

CASE_FILE = os.path.join(DATA_DIR, "phase5_case_cohort.csv")
REACTION_FILE = os.path.join(DATA_DIR, "phase5_case_reactions.csv")
SIGNAL_FILE = os.path.join(DATA_DIR, "phase5_signal_candidates.csv")
SUMMARY_FILE = os.path.join(DATA_DIR, "phase5_signal_summary.csv")

print("=" * 90)
print("PHASE 5 - PHARMACOVIGILANCE ANALYSIS VALIDATION")
print("=" * 90)


# =============================================================================
# FILE CHECK
# =============================================================================

print("\n" + "=" * 90)
print("FILE CHECK")
print("-" * 90)

files = {
    "phase5_case_cohort.csv": CASE_FILE,
    "phase5_case_reactions.csv": REACTION_FILE,
    "phase5_signal_candidates.csv": SIGNAL_FILE,
    "phase5_signal_summary.csv": SUMMARY_FILE,
}

for name, path in files.items():

    if os.path.exists(path):
        print(f"PASS - {name}")
    else:
        print(f"FAIL - {name} not found.")
        raise SystemExit(1)


# =============================================================================
# LOAD
# =============================================================================

cases = pd.read_csv(CASE_FILE)
reactions = pd.read_csv(REACTION_FILE)
signals = pd.read_csv(SIGNAL_FILE)
summary = pd.read_csv(SUMMARY_FILE)

print("\n" + "=" * 90)
print("DATASET SIZES")
print("-" * 90)

print(f"Case cohort rows       : {len(cases):,}")
print(f"Reaction rows          : {len(reactions):,}")
print(f"Signal candidates      : {len(signals):,}")
print(f"Summary rows           : {len(summary):,}")


# =============================================================================
# CASE VALIDATION
# =============================================================================

print("\n" + "=" * 90)
print("CASE COHORT VALIDATION")
print("-" * 90)

required_case_columns = [
    "safetyreportid",
    "bisoprolol_exposed",
    "drug_count",
    "reaction_count",
    "drug_products",
    "reaction_terms",
]

for column in required_case_columns:

    if column not in cases.columns:
        print(f"FAIL - Missing case column: {column}")
        raise SystemExit(1)

    print(f"PASS - {column}")


if cases["safetyreportid"].isna().any():
    print("FAIL - Missing safety report IDs.")
    raise SystemExit(1)

print("PASS - No missing case IDs.")


duplicates = cases["safetyreportid"].duplicated().sum()

if duplicates:
    print(f"FAIL - Duplicate cases: {duplicates}")
    raise SystemExit(1)

print("PASS - One row per case.")


# =============================================================================
# BISOPROLOL VALIDATION
# =============================================================================

print("\n" + "=" * 90)
print("BISOPROLOL COHORT VALIDATION")
print("-" * 90)

not_exposed = (
    cases["bisoprolol_exposed"]
    .astype(str)
    .str.lower()
    != "true"
)

if not_exposed.any():
    print(
        f"WARNING - {not_exposed.sum()} cases are not marked "
        "as Bisoprolol exposed."
    )
else:
    print("PASS - All cohort cases are Bisoprolol exposed.")


# =============================================================================
# REACTION VALIDATION
# =============================================================================

print("\n" + "=" * 90)
print("CASE × REACTION VALIDATION")
print("-" * 90)

required_reaction_columns = [
    "safetyreportid",
    "reaction_index",
    "reactionmeddrapt",
]

for column in required_reaction_columns:

    if column not in reactions.columns:
        print(f"FAIL - Missing reaction column: {column}")
        raise SystemExit(1)

    print(f"PASS - {column}")


if reactions["safetyreportid"].isna().any():
    print("FAIL - Missing reaction case IDs.")
    raise SystemExit(1)

print("PASS - No missing reaction case IDs.")


if reactions["reactionmeddrapt"].isna().any():
    print("FAIL - Missing reaction terms.")
    raise SystemExit(1)

print("PASS - No missing reaction terms.")


duplicates = reactions.duplicated(
    subset=["safetyreportid", "reaction_index"]
).sum()

if duplicates:
    print(f"FAIL - Duplicate case/reaction indexes: {duplicates}")
    raise SystemExit(1)

print("PASS - No duplicate case/reaction indexes.")


# =============================================================================
# CASE COVERAGE
# =============================================================================

print("\n" + "=" * 90)
print("CASE COVERAGE")
print("-" * 90)

case_ids = set(cases["safetyreportid"].astype(str))
reaction_case_ids = set(
    reactions["safetyreportid"].astype(str)
)

missing_reaction_cases = case_ids - reaction_case_ids

if missing_reaction_cases:
    print(
        f"WARNING - {len(missing_reaction_cases)} "
        "cases have no reaction records."
    )
else:
    print("PASS - Every cohort case has reaction records.")


# =============================================================================
# REACTION INDEX CONTINUITY
# =============================================================================

print("\n" + "=" * 90)
print("REACTION INDEX VALIDATION")
print("-" * 90)

bad_index_cases = 0

for case_id, group in reactions.groupby("safetyreportid"):

    indexes = sorted(
        group["reaction_index"]
        .astype(int)
        .tolist()
    )

    expected = list(range(len(indexes)))

    if indexes != expected:
        bad_index_cases += 1

if bad_index_cases:

    print(
        f"FAIL - Cases with non-contiguous reaction indexes: "
        f"{bad_index_cases}"
    )
    raise SystemExit(1)

print("PASS - Reaction indexes are contiguous.")


# =============================================================================
# EMBEDDED COMMA CHECK
# =============================================================================

print("\n" + "=" * 90)
print("EMBEDDED-COMMA REACTION CHECK")
print("-" * 90)

comma_reactions = reactions[
    reactions["reactionmeddrapt"]
    .astype(str)
    .str.contains(",", regex=False)
]

print(
    f"Reactions containing commas : "
    f"{len(comma_reactions):,}"
)

if len(comma_reactions):

    unique_terms = sorted(
        comma_reactions["reactionmeddrapt"]
        .unique()
    )

    for term in unique_terms:
        print(f"  {term}")

    print(
        "PASS - Embedded commas remain inside reaction terms."
    )


# =============================================================================
# SIGNAL VALIDATION
# =============================================================================

print("\n" + "=" * 90)
print("SIGNAL CANDIDATE VALIDATION")
print("-" * 90)

required_signal_columns = [
    "reactionmeddrapt",
    "case_count",
    "percentage_of_cases",
    "serious_case_count",
    "screening_rule",
    "analysis_type",
    "causality_established",
    "disproportionality_available",
]

for column in required_signal_columns:

    if column not in signals.columns:
        print(f"FAIL - Missing signal column: {column}")
        raise SystemExit(1)

    print(f"PASS - {column}")


invalid_threshold = (
    signals["case_count"] < 5
).sum()

if invalid_threshold:

    print(
        f"FAIL - {invalid_threshold} signal records "
        "below minimum threshold."
    )
    raise SystemExit(1)

print("PASS - All signal candidates meet minimum case threshold.")


# =============================================================================
# SAFETY CHECKS
# =============================================================================

print("\n" + "=" * 90)
print("ANALYTICAL SAFETY CHECKS")
print("-" * 90)

causality_values = (
    signals["causality_established"]
    .astype(str)
    .str.lower()
    .unique()
)

if set(causality_values) != {"false"}:

    print(
        "FAIL - Causality flag contains unexpected values."
    )
    raise SystemExit(1)

print("PASS - No candidate is marked as causally established.")


disproportionality_values = (
    signals["disproportionality_available"]
    .astype(str)
    .str.lower()
    .unique()
)

if set(disproportionality_values) != {"false"}:

    print(
        "FAIL - Disproportionality flag contains unexpected values."
    )
    raise SystemExit(1)

print(
    "PASS - No disproportionality result was "
    "calculated without a comparator."
)


# =============================================================================
# FINAL
# =============================================================================

print("\n" + "=" * 90)
print("FINAL RESULT: PASS")
print("=" * 90)

print("Phase 5 pharmacovigilance analysis is structurally valid.")

print("\nGenerated datasets:")
print("- phase5_case_cohort.csv")
print("- phase5_case_reactions.csv")
print("- phase5_signal_candidates.csv")
print("- phase5_signal_summary.csv")

print("\nPhase status:")
print("Phase 1 - Drug normalization       : COMPLETE")
print("Phase 2 - Reaction normalization   : COMPLETE")
print("Phase 3 - Structure validation     : COMPLETE")
print("Phase 4 - Case integration         : COMPLETE")
print("Phase 5 - Pharmacovigilance screen : COMPLETE")

print("\nIMPORTANT:")
print(
    "The current dataset contains no internal non-Bisoprolol "
    "comparator cohort."
)
print(
    "Therefore ROR/PRR has intentionally NOT been calculated."
)
print(
    "The signal candidates are exploratory frequency findings "
    "and do not establish causality."
)

print("=" * 90)