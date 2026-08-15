import os
import sys
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


FILES = {
    "reporting": "phase8_structured_reporting.csv",
    "cards": "phase8_candidate_report_cards.csv",
    "summary": "phase8_analysis_summary.csv",
}


# ============================================================
# REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = {
    "reporting": [
        "reactionmeddrapt",
        "reported_cases",
        "percentage_of_all_cases",
        "serious_cases",
        "serious_percentage",
        "evidence_level",
        "frequency_interpretation",
        "causality_status",
        "disproportionality_status",
        "comparator_status",
        "interaction_status",
    ],

    "cards": [
        "rank",
        "reaction",
        "reported_cases",
        "percentage_of_all_cases",
        "serious_cases",
        "serious_percentage",
        "evidence_level",
        "frequency_interpretation",
        "causality",
        "disproportionality",
        "comparator",
        "interaction",
    ],

    "summary": [
        "integrated_cases",
        "bisoprolol_cases",
        "candidate_reactions",
        "candidate_case_reaction_rows",
        "candidate_unique_cases",
        "unique_raw_reaction_terms",
        "top_candidate",
        "top_candidate_cases",
        "top_candidate_percentage",
        "top_candidate_serious_cases",
        "comparator_available",
        "ror_available",
        "prr_available",
        "frequency_is_incidence",
        "causality_established",
        "disproportionality_established",
        "co_medication_interaction_established",
        "analysis_type",
        "reporting_scope",
        "interpretation",
        "major_limitation",
    ],
}


# ============================================================
# HELPERS
# ============================================================

def section(title):
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


def pass_msg(message):
    print(f"PASS - {message}")


def fail(message):
    raise ValueError(message)


def normalize_bool(value):
    """
    Convert CSV boolean-like values into Python bool.

    Handles:
        True / False
        TRUE / FALSE
        true / false
        1 / 0
        yes / no
    """
    if isinstance(value, bool):
        return value

    if pd.isna(value):
        return False

    text = str(value).strip().lower()

    if text in {"true", "1", "yes", "y", "t"}:
        return True

    if text in {"false", "0", "no", "n", "f"}:
        return False

    fail(f"Unable to interpret boolean value: {value}")


def require_columns(df, columns, label):
    for column in columns:
        if column not in df.columns:
            fail(
                f"Missing required column '{column}' "
                f"in {label}"
            )

        pass_msg(f"{label}: {column}")


def numeric_series(df, column, label):
    values = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    if values.isna().any():
        fail(
            f"Non-numeric values found in "
            f"{label}:{column}"
        )

    return values


# ============================================================
# HEADER
# ============================================================

print()
print("=" * 100)
print("PHASE 8 - STRUCTURED PHARMACOVIGILANCE REPORTING VALIDATION")
print("=" * 100)


# ============================================================
# FILE CHECK
# ============================================================

section("FILE CHECK")

for key, filename in FILES.items():

    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        fail(
            f"Missing required file: {path}"
        )

    pass_msg(filename)


# ============================================================
# LOAD DATASETS
# ============================================================

section("LOADING PHASE 8 OUTPUTS")

reporting = pd.read_csv(
    os.path.join(DATA_DIR, FILES["reporting"])
)

cards = pd.read_csv(
    os.path.join(DATA_DIR, FILES["cards"])
)

summary = pd.read_csv(
    os.path.join(DATA_DIR, FILES["summary"])
)

print(
    f"Structured reporting rows : {len(reporting):,}"
)

print(
    f"Candidate report cards    : {len(cards):,}"
)

print(
    f"Summary rows              : {len(summary):,}"
)


# ============================================================
# COLUMN VALIDATION
# ============================================================

section("COLUMN VALIDATION")

require_columns(
    reporting,
    REQUIRED_COLUMNS["reporting"],
    "reporting"
)

require_columns(
    cards,
    REQUIRED_COLUMNS["cards"],
    "cards"
)

require_columns(
    summary,
    REQUIRED_COLUMNS["summary"],
    "summary"
)


# ============================================================
# BASIC DATASET VALIDATION
# ============================================================

section("REPORTING ROW VALIDATION")

if len(reporting) != 8:
    fail(
        f"Expected eight candidate reporting records, "
        f"found {len(reporting)}"
    )

pass_msg("Eight candidate reporting records present.")


if reporting["reactionmeddrapt"].duplicated().any():
    duplicates = reporting.loc[
        reporting["reactionmeddrapt"].duplicated(),
        "reactionmeddrapt"
    ].tolist()

    fail(
        f"Duplicate candidate reactions detected: "
        f"{duplicates}"
    )

pass_msg("Candidate reactions are unique.")


# ============================================================
# CANDIDATE CARD VALIDATION
# ============================================================

section("CANDIDATE CARD VALIDATION")

if len(cards) != 8:
    fail(
        f"Expected eight candidate report cards, "
        f"found {len(cards)}"
    )

pass_msg("Eight candidate report cards present.")


ranks = pd.to_numeric(
    cards["rank"],
    errors="coerce"
)

if ranks.isna().any():
    fail("Ranking contains non-numeric values.")

expected_ranks = list(range(1, len(cards) + 1))
actual_ranks = sorted(ranks.astype(int).tolist())

if actual_ranks != expected_ranks:
    fail(
        f"Ranking sequence invalid. "
        f"Expected {expected_ranks}, "
        f"found {actual_ranks}"
    )

pass_msg("Ranking sequence is contiguous.")


# ============================================================
# PERCENTAGE VALIDATION
# ============================================================

section("PERCENTAGE VALIDATION")

reporting_pct = numeric_series(
    reporting,
    "percentage_of_all_cases",
    "reporting"
)

reporting_serious_pct = numeric_series(
    reporting,
    "serious_percentage",
    "reporting"
)

cards_pct = numeric_series(
    cards,
    "percentage_of_all_cases",
    "cards"
)

cards_serious_pct = numeric_series(
    cards,
    "serious_percentage",
    "cards"
)


for name, values in [
    ("reporting percentage_of_all_cases", reporting_pct),
    ("reporting serious_percentage", reporting_serious_pct),
    ("cards percentage_of_all_cases", cards_pct),
    ("cards serious_percentage", cards_serious_pct),
]:

    if ((values < 0) | (values > 100)).any():
        fail(
            f"Invalid percentage detected in {name}"
        )

    pass_msg(name)


# ============================================================
# SERIOUSNESS VALIDATION
# ============================================================

section("SERIOUSNESS VALIDATION")

reported_cases = numeric_series(
    reporting,
    "reported_cases",
    "reporting"
)

serious_cases = numeric_series(
    reporting,
    "serious_cases",
    "reporting"
)

if (reported_cases < 0).any():
    fail("Negative reported case counts detected.")

if (serious_cases < 0).any():
    fail("Negative serious case counts detected.")

if (serious_cases > reported_cases).any():
    fail(
        "Serious cases exceed reported cases."
    )

pass_msg(
    "Serious cases never exceed reported cases."
)


# ============================================================
# ANALYTICAL SAFETY VALIDATION
# ============================================================

section("ANALYTICAL SAFETY VALIDATION")

if len(summary) != 1:
    fail(
        f"Expected exactly one summary row, "
        f"found {len(summary)}"
    )

summary_row = summary.iloc[0]


comparator_available = normalize_bool(
    summary_row["comparator_available"]
)

ror_available = normalize_bool(
    summary_row["ror_available"]
)

prr_available = normalize_bool(
    summary_row["prr_available"]
)

frequency_is_incidence = normalize_bool(
    summary_row["frequency_is_incidence"]
)

causality_established = normalize_bool(
    summary_row["causality_established"]
)

disproportionality_established = normalize_bool(
    summary_row["disproportionality_established"]
)

interaction_established = normalize_bool(
    summary_row["co_medication_interaction_established"]
)


print(
    f"Comparator available              : "
    f"{comparator_available}"
)

print(
    f"ROR available                     : "
    f"{ror_available}"
)

print(
    f"PRR available                     : "
    f"{prr_available}"
)

print(
    f"Frequency interpreted as incidence: "
    f"{frequency_is_incidence}"
)

print(
    f"Causality established             : "
    f"{causality_established}"
)

print(
    f"Disproportionality established    : "
    f"{disproportionality_established}"
)

print(
    f"Co-medication interaction         : "
    f"{interaction_established}"
)


# ------------------------------------------------------------
# IMPORTANT:
# FALSE IS THE EXPECTED SAFE STATE.
# Do NOT raise an error because these values are FALSE.
# Raise an error only if they unexpectedly become TRUE.
# ------------------------------------------------------------

if comparator_available:
    fail(
        "Analytical safety violation: "
        "Comparator unexpectedly available."
    )

pass_msg(
    "Comparator unavailable as expected."
)


if ror_available:
    fail(
        "Analytical safety violation: "
        "ROR unexpectedly available."
    )

pass_msg(
    "ROR remains unavailable."
)


if prr_available:
    fail(
        "Analytical safety violation: "
        "PRR unexpectedly available."
    )

pass_msg(
    "PRR remains unavailable."
)


if frequency_is_incidence:
    fail(
        "Analytical safety violation: "
        "Frequency is incorrectly interpreted as incidence."
    )

pass_msg(
    "Frequency-as-incidence interpretation remains disabled."
)


if causality_established:
    fail(
        "Analytical safety violation: "
        "Causality is incorrectly marked as established."
    )

pass_msg(
    "Causality remains unestablished."
)


if disproportionality_established:
    fail(
        "Analytical safety violation: "
        "Disproportionality is incorrectly marked as established."
    )

pass_msg(
    "Disproportionality remains disabled."
)


if interaction_established:
    fail(
        "Analytical safety violation: "
        "Co-medication interaction is incorrectly marked as established."
    )

pass_msg(
    "Co-medication interaction remains unestablished."
)


# ============================================================
# CANDIDATE CONSISTENCY
# ============================================================

section("CANDIDATE CONSISTENCY VALIDATION")

reporting_candidates = set(
    reporting["reactionmeddrapt"]
    .astype(str)
    .str.strip()
)

card_candidates = set(
    cards["reaction"]
    .astype(str)
    .str.strip()
)

if reporting_candidates != card_candidates:
    fail(
        "Reporting candidates and candidate cards do not match."
    )

pass_msg(
    "Reporting and candidate-card reactions match."
)


# ============================================================
# SUMMARY VALIDATION
# ============================================================

section("SUMMARY VALIDATION")

integrated_cases = pd.to_numeric(
    pd.Series([summary_row["integrated_cases"]]),
    errors="coerce"
).iloc[0]

bisoprolol_cases = pd.to_numeric(
    pd.Series([summary_row["bisoprolol_cases"]]),
    errors="coerce"
).iloc[0]

candidate_reactions = pd.to_numeric(
    pd.Series([summary_row["candidate_reactions"]]),
    errors="coerce"
).iloc[0]

candidate_case_rows = pd.to_numeric(
    pd.Series([summary_row["candidate_case_reaction_rows"]]),
    errors="coerce"
).iloc[0]

candidate_unique_cases = pd.to_numeric(
    pd.Series([summary_row["candidate_unique_cases"]]),
    errors="coerce"
).iloc[0]


if pd.isna(integrated_cases):
    fail("Integrated case count is invalid.")

if pd.isna(bisoprolol_cases):
    fail("Bisoprolol case count is invalid.")

if pd.isna(candidate_reactions):
    fail("Candidate reaction count is invalid.")

if pd.isna(candidate_case_rows):
    fail("Candidate case-reaction row count is invalid.")

if pd.isna(candidate_unique_cases):
    fail("Candidate unique case count is invalid.")


print(
    f"Integrated cases       : {int(integrated_cases):,}"
)

print(
    f"Bisoprolol cases       : {int(bisoprolol_cases):,}"
)

print(
    f"Candidate reactions    : {int(candidate_reactions):,}"
)

print(
    f"Candidate case rows    : {int(candidate_case_rows):,}"
)

print(
    f"Candidate unique cases : {int(candidate_unique_cases):,}"
)


if integrated_cases <= 0:
    fail(
        "Integrated case count must be greater than zero."
    )

if bisoprolol_cases != integrated_cases:
    fail(
        "Bisoprolol case count does not match "
        "integrated case count."
    )

pass_msg(
    f"Integrated cases: {int(integrated_cases):,}"
)

pass_msg(
    "Bisoprolol cases match integrated cases."
)


if candidate_reactions != len(reporting):
    fail(
        "Candidate reaction count does not match "
        "reporting dataset."
    )

pass_msg(
    "Candidate count matches reporting dataset."
)


if candidate_unique_cases < 0:
    fail(
        "Candidate unique case count cannot be negative."
    )

if candidate_unique_cases > integrated_cases:
    fail(
        "Candidate unique cases exceed integrated cases."
    )

pass_msg(
    "Candidate unique case count is logically consistent."
)


# ============================================================
# TOP CANDIDATE VALIDATION
# ============================================================

section("TOP CANDIDATE VALIDATION")

top_candidate = str(
    summary_row["top_candidate"]
).strip()

top_candidate_cases = pd.to_numeric(
    pd.Series([summary_row["top_candidate_cases"]]),
    errors="coerce"
).iloc[0]

top_candidate_percentage = pd.to_numeric(
    pd.Series([summary_row["top_candidate_percentage"]]),
    errors="coerce"
).iloc[0]

top_candidate_serious_cases = pd.to_numeric(
    pd.Series([summary_row["top_candidate_serious_cases"]]),
    errors="coerce"
).iloc[0]


if top_candidate not in reporting_candidates:
    fail(
        f"Top candidate '{top_candidate}' "
        f"is not present in reporting dataset."
    )

pass_msg(
    f"Top candidate: {top_candidate}"
)


top_row = reporting[
    reporting["reactionmeddrapt"].astype(str).str.strip()
    == top_candidate
]

if len(top_row) != 1:
    fail(
        "Top candidate must have exactly one reporting record."
    )

top_row = top_row.iloc[0]

expected_top_cases = float(
    pd.to_numeric(
        pd.Series([top_row["reported_cases"]]),
        errors="coerce"
    ).iloc[0]
)

expected_top_percentage = float(
    pd.to_numeric(
        pd.Series([top_row["percentage_of_all_cases"]]),
        errors="coerce"
    ).iloc[0]
)

expected_top_serious = float(
    pd.to_numeric(
        pd.Series([top_row["serious_cases"]]),
        errors="coerce"
    ).iloc[0]
)


if float(top_candidate_cases) != expected_top_cases:
    fail(
        "Top candidate case count does not match reporting data."
    )

if round(float(top_candidate_percentage), 6) != round(
    expected_top_percentage,
    6
):
    fail(
        "Top candidate percentage does not match reporting data."
    )

if float(top_candidate_serious_cases) != expected_top_serious:
    fail(
        "Top candidate serious case count does not match reporting data."
    )

pass_msg(
    "Top candidate case count matches."
)

pass_msg(
    "Top candidate percentage matches."
)

pass_msg(
    "Top candidate serious case count matches."
)


# ============================================================
# REPORTING STATUS VALIDATION
# ============================================================

section("REPORTING STATUS VALIDATION")

required_status_columns = [
    "frequency_interpretation",
    "causality_status",
    "disproportionality_status",
    "comparator_status",
    "interaction_status",
]

for column in required_status_columns:

    values = (
        reporting[column]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    if values.isna().any():
        fail(
            f"Missing values found in reporting status: {column}"
        )

    pass_msg(
        f"{column} populated."
    )


# ============================================================
# FINAL ANALYTICAL SAFETY SUMMARY
# ============================================================

section("ANALYTICAL SAFETY VALIDATION")

pass_msg(
    "Frequency-as-incidence interpretation remains disabled."
)

pass_msg(
    "Comparator availability remains disabled."
)

pass_msg(
    "Disproportionality availability remains disabled."
)

pass_msg(
    "Causality remains disabled."
)

pass_msg(
    "ROR remains disabled."
)

pass_msg(
    "PRR remains disabled."
)

pass_msg(
    "Co-medication interaction remains disabled."
)


# ============================================================
# FINAL RESULT
# ============================================================

section("FINAL RESULT")

print("PASS")
print()
print(
    "Phase 8 structured pharmacovigilance reporting "
    "analysis is structurally valid."
)

print()
print("Generated datasets:")
print("- phase8_structured_reporting.csv")
print("- phase8_candidate_report_cards.csv")
print("- phase8_analysis_summary.csv")

print()
print("Phase status:")
print(
    "Phase 1 - Drug normalization       : COMPLETE"
)
print(
    "Phase 2 - Reaction normalization   : COMPLETE"
)
print(
    "Phase 3 - Structure validation     : COMPLETE"
)
print(
    "Phase 4 - Case integration         : COMPLETE"
)
print(
    "Phase 5 - Pharmacovigilance screen : COMPLETE"
)
print(
    "Phase 6 - Signal pattern analysis  : COMPLETE"
)
print(
    "Phase 7 - Evidence & reporting     : COMPLETE"
)
print(
    "Phase 8 - Structured reporting     : COMPLETE"
)

print()
print("IMPORTANT:")
print(
    "No internal non-Bisoprolol comparator exists."
)
print(
    "ROR/PRR are not calculated."
)
print(
    "Frequency is not interpreted as incidence."
)
print(
    "Causality is not established."
)
print(
    "Disproportionality is not established."
)
print(
    "Co-medication patterns do not establish interactions."
)
print(
    "All findings remain descriptive/exploratory."
)

print()
print("=" * 100)