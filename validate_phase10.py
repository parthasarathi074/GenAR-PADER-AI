import os
import json
import sys


# =============================================================================
# PHASE 10 - CONTROLLED PHARMACOVIGILANCE REPORT VALIDATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

CONTEXT_FILE = os.path.join(DATA_DIR, "phase10_genai_context.json")
CANDIDATE_CONTEXT_FILE = os.path.join(
    DATA_DIR, "phase10_candidate_context.json"
)
RULES_FILE = os.path.join(DATA_DIR, "phase10_reporting_rules.json")
TEXT_REPORT_FILE = os.path.join(
    DATA_DIR, "phase10_pharmacovigilance_report.txt"
)
JSON_REPORT_FILE = os.path.join(
    DATA_DIR, "phase10_generated_report.json"
)


# =============================================================================
# HELPERS
# =============================================================================

def section(title):
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


def pass_msg(message):
    print(f"PASS - {message}")


def fail(message):
    print(f"FAIL - {message}")
    sys.exit(1)


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        fail(
            f"Unable to read {os.path.basename(path)}: {exc}"
        )


def load_text(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as exc:
        fail(
            f"Unable to read {os.path.basename(path)}: {exc}"
        )


def normalize_bool(value):
    """
    Safely convert common representations to boolean.

    True examples:
        True, "true", "yes", "1"

    False examples:
        False, "false", "no", "0"
    """
    if isinstance(value, bool):
        return value

    if value is None:
        return None

    if isinstance(value, (int, float)):
        if value == 1:
            return True
        if value == 0:
            return False

    text = str(value).strip().lower()

    if text in {"true", "yes", "1"}:
        return True

    if text in {"false", "no", "0"}:
        return False

    return None


def require_false(mapping, key, location):
    if key not in mapping:
        fail(
            f"{location} missing analytical safety flag: {key}"
        )

    value = normalize_bool(mapping.get(key))

    if value is not False:
        fail(
            f"{location} analytical safety violation: "
            f"{key}={mapping.get(key)!r}"
        )

    pass_msg(
        f"{location} {key} remains False."
    )


# =============================================================================
# START
# =============================================================================

section(
    "PHASE 10 - CONTROLLED PHARMACOVIGILANCE REPORT VALIDATION"
)


# =============================================================================
# FILE CHECK
# =============================================================================

section("FILE CHECK")

required_files = [
    CONTEXT_FILE,
    CANDIDATE_CONTEXT_FILE,
    RULES_FILE,
    TEXT_REPORT_FILE,
    JSON_REPORT_FILE,
]

for path in required_files:

    if not os.path.exists(path):
        fail(
            f"Required file missing: {os.path.basename(path)}"
        )

    if os.path.getsize(path) == 0:
        fail(
            f"Required file is empty: {os.path.basename(path)}"
        )

    pass_msg(os.path.basename(path))


# =============================================================================
# LOAD FILES
# =============================================================================

section("LOADING PHASE 10 OUTPUTS")

context = load_json(CONTEXT_FILE)
candidate_context = load_json(CANDIDATE_CONTEXT_FILE)
rules = load_json(RULES_FILE)
generated_report = load_json(JSON_REPORT_FILE)
text_report = load_text(TEXT_REPORT_FILE)

context_candidates = context.get("candidates", [])
candidate_file_candidates = candidate_context.get("candidates", [])
generated_candidates = generated_report.get("candidates", [])

print(
    f"Context version      : "
    f"{context.get('context_version')}"
)
print(
    f"Context candidates   : "
    f"{len(context_candidates)}"
)
print(
    f"Candidate file count : "
    f"{len(candidate_file_candidates)}"
)
print(
    f"Generated candidates : "
    f"{len(generated_candidates)}"
)
print(
    f"Text report length   : "
    f"{len(text_report):,} characters"
)


# =============================================================================
# CONTEXT VERSION VALIDATION
# =============================================================================

section("CONTEXT VERSION VALIDATION")

if context.get("context_version") != "phase10_v1":
    fail(
        "Unexpected context version: "
        f"{context.get('context_version')}"
    )

pass_msg("Context version is phase10_v1.")


if generated_report.get("report_version") != "phase10_report_v1":
    fail(
        "Unexpected report version: "
        f"{generated_report.get('report_version')}"
    )

pass_msg("Report version is phase10_report_v1.")


# =============================================================================
# DATASET SUMMARY VALIDATION
# =============================================================================

section("DATASET SUMMARY VALIDATION")

dataset = context.get("dataset_summary", {})
generated_dataset = generated_report.get(
    "dataset_summary", {}
)

expected_values = {
    "integrated_cases": 1024,
    "bisoprolol_cases": 1024,
    "candidate_reactions": 8,
    "higher_priority_candidates": 1,
    "moderate_priority_candidates": 2,
    "lower_priority_candidates": 5,
    "top_candidate": "Acute kidney injury",
    "top_candidate_cases": 22,
    "top_candidate_priority": "higher_priority_candidate",
}

for key, expected in expected_values.items():

    actual = dataset.get(key)

    if actual != expected:
        fail(
            f"{key}: expected {expected!r}, "
            f"found {actual!r}"
        )

    pass_msg(f"{key}: {expected}")


for key, expected in expected_values.items():

    actual = generated_dataset.get(key)

    if actual != expected:
        fail(
            f"Generated report dataset mismatch for "
            f"{key}: expected {expected!r}, "
            f"found {actual!r}"
        )

pass_msg(
    "Generated report dataset summary matches context."
)


# =============================================================================
# CANDIDATE COUNT VALIDATION
# =============================================================================

section("CANDIDATE COUNT VALIDATION")

if len(context_candidates) != 8:
    fail(
        f"Expected 8 context candidates, "
        f"found {len(context_candidates)}."
    )

pass_msg("Master context contains 8 candidates.")


if len(candidate_file_candidates) != 8:
    fail(
        f"Expected 8 candidate-context candidates, "
        f"found {len(candidate_file_candidates)}."
    )

pass_msg("Candidate context contains 8 candidates.")


if len(generated_candidates) != 8:
    fail(
        f"Expected 8 generated-report candidates, "
        f"found {len(generated_candidates)}."
    )

pass_msg("Generated report contains 8 candidates.")


# =============================================================================
# CANDIDATE CONSISTENCY VALIDATION
# =============================================================================

section("CANDIDATE CONSISTENCY VALIDATION")

try:
    context_names = {
        candidate["reaction"]
        for candidate in context_candidates
    }

    candidate_file_names = {
        candidate["reaction"]
        for candidate in candidate_file_candidates
    }

    generated_names = {
        candidate["reaction"]
        for candidate in generated_candidates
    }

except KeyError as exc:
    fail(
        f"Candidate structure missing field: {exc}"
    )


if context_names != candidate_file_names:
    fail(
        "Master and candidate-context reaction sets differ."
    )

pass_msg(
    "Master and candidate-context reaction sets match."
)


if context_names != generated_names:
    fail(
        "Master context and generated-report reaction sets differ."
    )

pass_msg(
    "Master context and generated-report reaction sets match."
)


# =============================================================================
# DUPLICATE CANDIDATE CHECK
# =============================================================================

section("DUPLICATE CANDIDATE VALIDATION")

if len(context_names) != len(context_candidates):
    fail(
        "Duplicate candidate reaction found in master context."
    )

if len(candidate_file_names) != len(candidate_file_candidates):
    fail(
        "Duplicate candidate reaction found in candidate context."
    )

if len(generated_names) != len(generated_candidates):
    fail(
        "Duplicate candidate reaction found in generated report."
    )

pass_msg(
    "No duplicate candidate reactions detected."
)


# =============================================================================
# RANK VALIDATION
# =============================================================================

section("RANK VALIDATION")

try:
    actual_ranks = sorted(
        int(item["rank"])
        for item in generated_candidates
    )

except (KeyError, TypeError, ValueError):
    fail(
        "Generated candidate ranking contains invalid values."
    )

expected_ranks = list(range(1, 9))

if actual_ranks != expected_ranks:
    fail(
        f"Invalid candidate ranking: {actual_ranks}"
    )

pass_msg(
    "Candidate ranking is contiguous from 1 to 8."
)


# =============================================================================
# EXPECTED CANDIDATE VALUES
# =============================================================================

section("CANDIDATE VALUE VALIDATION")

expected_candidates = {
    "Acute kidney injury": {
        "rank": 1,
        "reported_cases": 22,
        "review_priority": "higher_priority_candidate",
    },
    "Drug ineffective": {
        "rank": 2,
        "reported_cases": 11,
        "review_priority": "moderate_priority_candidate",
    },
    "Cholestasis": {
        "rank": 3,
        "reported_cases": 6,
        "review_priority": "lower_priority_candidate",
    },
    "Hypokalaemia": {
        "rank": 4,
        "reported_cases": 6,
        "review_priority": "moderate_priority_candidate",
    },
    "Hyponatraemia": {
        "rank": 5,
        "reported_cases": 6,
        "review_priority": "lower_priority_candidate",
    },
    "Drug interaction": {
        "rank": 6,
        "reported_cases": 5,
        "review_priority": "lower_priority_candidate",
    },
    "Hepatic cytolysis": {
        "rank": 7,
        "reported_cases": 5,
        "review_priority": "lower_priority_candidate",
    },
    "Joint swelling": {
        "rank": 8,
        "reported_cases": 5,
        "review_priority": "lower_priority_candidate",
    },
}


generated_lookup = {
    item.get("reaction"): item
    for item in generated_candidates
}


for reaction, expected in expected_candidates.items():

    if reaction not in generated_lookup:
        fail(
            f"Missing candidate: {reaction}"
        )

    actual = generated_lookup[reaction]

    try:
        actual_rank = int(actual.get("rank"))
        actual_cases = int(actual.get("reported_cases"))
    except (TypeError, ValueError):
        fail(
            f"{reaction}: invalid numerical candidate data."
        )

    if actual_rank != expected["rank"]:
        fail(
            f"{reaction}: expected rank "
            f"{expected['rank']}, found {actual_rank}."
        )

    if actual_cases != expected["reported_cases"]:
        fail(
            f"{reaction}: expected "
            f"{expected['reported_cases']} cases, "
            f"found {actual_cases}."
        )

    if (
        actual.get("review_priority")
        != expected["review_priority"]
    ):
        fail(
            f"{reaction}: priority mismatch. "
            f"Expected {expected['review_priority']!r}, "
            f"found {actual.get('review_priority')!r}."
        )

    pass_msg(
        f"{reaction}: values match."
    )


# =============================================================================
# ANALYTICAL SAFETY VALIDATION
# =============================================================================

section("ANALYTICAL SAFETY VALIDATION")

analytical_safety = context.get(
    "analytical_safety", {}
)

generated_safety = generated_report.get(
    "analytical_safety", {}
)

final_interpretation = generated_report.get(
    "final_interpretation", {}
)


false_flags = [
    "comparator_available",
    "ror_available",
    "prr_available",
    "frequency_is_incidence",
    "causality_established",
    "disproportionality_established",
    "confirmed_signal_established",
    "drug_interaction_established",
]


for flag in false_flags:
    require_false(
        analytical_safety,
        flag,
        "context"
    )


for flag in false_flags:
    require_false(
        generated_safety,
        flag,
        "generated report"
    )


final_false_flags = [
    "frequency_is_incidence",
    "causality_established",
    "disproportionality_established",
    "confirmed_signal_established",
    "drug_interaction_established",
    "ror_available",
    "prr_available",
]


for flag in final_false_flags:
    require_false(
        final_interpretation,
        flag,
        "final interpretation"
    )


pass_msg(
    "All analytical safety restrictions are preserved."
)


# =============================================================================
# CANDIDATE SAFETY VALIDATION
# =============================================================================

section("CANDIDATE SAFETY VALIDATION")

candidate_false_flags = [
    "confirmed_signal",
    "confirmed_adverse_reaction",
    "causality_established",
    "disproportionality_established",
    "incidence_established",
    "interaction_established",
]


for candidate in generated_candidates:

    reaction = candidate.get(
        "reaction", "[UNKNOWN]"
    )

    for flag in candidate_false_flags:

        if flag not in candidate:
            fail(
                f"{reaction}: missing candidate safety "
                f"field {flag}."
            )

        value = normalize_bool(
            candidate.get(flag)
        )

        if value is not False:
            fail(
                f"{reaction}: {flag} must remain False; "
                f"found {candidate.get(flag)!r}."
            )


pass_msg(
    "All candidate prohibited conclusions remain False."
)


# =============================================================================
# TEXT REPORT SECTION VALIDATION
# =============================================================================

section("TEXT REPORT SECTION VALIDATION")

required_sections = [
    "1. EXECUTIVE SUMMARY",
    "2. DATASET OVERVIEW",
    "3. METHODOLOGY OVERVIEW",
    "4. CANDIDATE REVIEW PRIORITY SUMMARY",
    "5. CANDIDATE-BY-CANDIDATE EVIDENCE",
    "6. SERIOUSNESS ASSESSMENT",
    "7. RECOMMENDED FOLLOW-UP ACTIONS",
    "8. ANALYTICAL LIMITATIONS",
    "9. INTERPRETATION BOUNDARIES",
    "10. FINAL PHARMACOVIGILANCE SUMMARY",
]


for report_section in required_sections:

    if report_section not in text_report:
        fail(
            f"Missing report section: {report_section}"
        )

    pass_msg(report_section)


# =============================================================================
# TEXT CANDIDATE COVERAGE
# =============================================================================

section("TEXT CANDIDATE COVERAGE")

for reaction in expected_candidates:

    if reaction not in text_report:
        fail(
            f"Candidate missing from text report: "
            f"{reaction}"
        )

    pass_msg(reaction)


# =============================================================================
# NUMERICAL COVERAGE VALIDATION
# =============================================================================

section("NUMERICAL COVERAGE VALIDATION")

required_text_values = [
    "1,024",
    "22",
    "11",
    "2.15%",
    "1.07%",
    "0.59%",
    "0.49%",
]


for value in required_text_values:

    if value not in text_report:
        fail(
            f"Expected value missing from report: "
            f"{value}"
        )

    pass_msg(
        f"Report contains {value}"
    )


# =============================================================================
# LIMITATION VALIDATION
# =============================================================================

section("LIMITATION VALIDATION")

limitations = generated_report.get(
    "limitations", []
)

if len(limitations) != 5:
    fail(
        f"Expected 5 limitations, "
        f"found {len(limitations)}."
    )

pass_msg(
    "Five analytical limitations retained."
)


required_limitation_fields = [
    "limitation_id",
    "limitation",
    "impact",
    "restriction",
]


for index, limitation in enumerate(
    limitations,
    start=1
):

    for field in required_limitation_fields:

        if field not in limitation:
            fail(
                f"Limitation {index} missing field: "
                f"{field}"
            )

        if limitation.get(field) in {
            None,
            ""
        }:
            fail(
                f"Limitation {index} has empty field: "
                f"{field}"
            )


pass_msg(
    "All limitation structures are complete."
)


# =============================================================================
# REPORTING RULE VALIDATION
# =============================================================================

section("REPORTING RULE VALIDATION")

required_rule_keys = [
    "role",
    "allowed_tasks",
    "prohibited_tasks",
    "required_language",
    "numerical_integrity",
    "interpretation_scope",
]


for key in required_rule_keys:

    if key not in rules:
        fail(
            f"Reporting rules missing: {key}"
        )

    pass_msg(
        f"Reporting rule present: {key}"
    )


# =============================================================================
# PROHIBITED POSITIVE CLAIM VALIDATION
# =============================================================================

section("PROHIBITED POSITIVE CLAIM VALIDATION")

lower_text = text_report.lower()


# IMPORTANT:
# Do NOT prohibit generic substrings such as:
#
#     "confirmed adverse reaction"
#
# because a valid safety sentence may say:
#
#     "not a confirmed adverse reaction"
#
# The checks below target affirmative/causal conclusions instead.

prohibited_positive_phrases = [
    "bisoprolol causes acute kidney injury",
    "bisoprolol causes drug ineffective",
    "bisoprolol causes cholestasis",
    "bisoprolol causes hypokalaemia",
    "bisoprolol causes hyponatraemia",
    "bisoprolol causes hepatic cytolysis",
    "causal relationship was established",
    "causal relationship has been established",
    "causality was established",
    "causality has been established",
    "a confirmed safety signal was established",
    "confirmed safety signal was established",
    "a safety signal was confirmed",
    "safety signal has been confirmed",
    "disproportionality was established",
    "disproportionality has been established",
    "ror demonstrates an association",
    "ror demonstrates association",
    "prr demonstrates an association",
    "prr demonstrates association",
    "drug-drug interaction was confirmed",
    "drug interaction was confirmed",
    "interaction was established",
    "interaction has been established",
]


detected_unsafe_phrases = []

for phrase in prohibited_positive_phrases:

    if phrase in lower_text:
        detected_unsafe_phrases.append(
            phrase
        )


if detected_unsafe_phrases:

    print(
        "Unsafe affirmative analytical statements detected:"
    )

    for phrase in detected_unsafe_phrases:
        print(f"  - {phrase}")

    fail(
        "Text report contains prohibited positive "
        "analytical conclusions."
    )


pass_msg(
    "No prohibited positive analytical claims detected."
)


# =============================================================================
# REQUIRED SAFETY LANGUAGE VALIDATION
# =============================================================================

section("REQUIRED SAFETY LANGUAGE VALIDATION")


# Use multiple acceptable alternatives because safe scientific
# wording can vary while preserving the same interpretation.

required_safety_concepts = {
    "incidence restriction": [
        "reported frequencies are not incidence estimates",
        "frequency is not interpreted as incidence",
        "frequencies are not incidence estimates",
        "frequency does not establish incidence",
    ],

    "causality restriction": [
        "no causal relationship",
        "causality is not established",
        "causality has not been established",
        "causal relationship is not established",
    ],

    "ROR restriction": [
        "ror has not been calculated",
        "ror was not calculated",
        "ror is not calculated",
        "ror not calculated",
    ],

    "PRR restriction": [
        "prr has not been calculated",
        "prr was not calculated",
        "prr is not calculated",
        "prr not calculated",
    ],

    "signal restriction": [
        "candidate reactions are not confirmed safety signals",
        "candidates are not confirmed safety signals",
        "no confirmed safety signal",
        "confirmed safety signal has not been established",
    ],

    "review priority restriction": [
        "review-priority classifications are triage categories only",
        "review priority classifications are triage categories only",
        "review priorities are triage categories only",
        "priority classifications represent review priority only",
    ],
}


for concept, alternatives in required_safety_concepts.items():

    found = any(
        phrase in lower_text
        for phrase in alternatives
    )

    if not found:
        fail(
            f"Required safety concept missing: {concept}"
        )

    pass_msg(concept)


# =============================================================================
# SAFE NEGATION VALIDATION
# =============================================================================

section("SAFE NEGATION VALIDATION")


# These phrases are explicitly SAFE.
# Their presence must never be treated as a failure.

safe_negated_phrases = [
    "not confirmed adverse reaction",
    "not a confirmed adverse reaction",
    "not confirmed adverse reactions",
    "not confirmed safety signal",
    "not a confirmed safety signal",
    "not confirmed safety signals",
    "causality is not established",
    "causality has not been established",
    "disproportionality is not established",
    "interaction is not established",
]


safe_found = [
    phrase
    for phrase in safe_negated_phrases
    if phrase in lower_text
]


print(
    f"Safe negated statements detected : "
    f"{len(safe_found)}"
)

for phrase in safe_found:
    print(f"  SAFE - {phrase}")


pass_msg(
    "Negated safety language is permitted and "
    "is not treated as an unsafe conclusion."
)


# =============================================================================
# REPORT/JSON NUMERICAL CONSISTENCY
# =============================================================================

section("REPORT / JSON NUMERICAL CONSISTENCY")

for reaction, expected in expected_candidates.items():

    candidate = generated_lookup[reaction]

    expected_cases = str(
        expected["reported_cases"]
    )

    if expected_cases not in text_report:
        fail(
            f"Case count for {reaction} is not "
            f"represented in the text report."
        )


pass_msg(
    "Candidate case counts are represented in "
    "the text report."
)


# =============================================================================
# TOP CANDIDATE VALIDATION
# =============================================================================

section("TOP CANDIDATE VALIDATION")

top_candidate = generated_lookup.get(
    "Acute kidney injury"
)

if top_candidate is None:
    fail(
        "Top candidate Acute kidney injury missing."
    )


if int(top_candidate.get("rank")) != 1:
    fail(
        "Acute kidney injury is not ranked first."
    )

pass_msg(
    "Top candidate: Acute kidney injury"
)


if int(top_candidate.get("reported_cases")) != 22:
    fail(
        "Top candidate case count mismatch."
    )

pass_msg(
    "Top candidate reported cases: 22"
)


if (
    top_candidate.get("review_priority")
    != "higher_priority_candidate"
):
    fail(
        "Top candidate priority mismatch."
    )

pass_msg(
    "Top candidate priority: "
    "higher_priority_candidate"
)


# =============================================================================
# PRIORITY DISTRIBUTION VALIDATION
# =============================================================================

section("PRIORITY DISTRIBUTION VALIDATION")

priority_counts = {}

for candidate in generated_candidates:

    priority = candidate.get(
        "review_priority"
    )

    priority_counts[priority] = (
        priority_counts.get(priority, 0) + 1
    )


expected_priority_counts = {
    "higher_priority_candidate": 1,
    "moderate_priority_candidate": 2,
    "lower_priority_candidate": 5,
}


for priority, expected_count in (
    expected_priority_counts.items()
):

    actual_count = priority_counts.get(
        priority, 0
    )

    if actual_count != expected_count:
        fail(
            f"{priority}: expected "
            f"{expected_count}, found "
            f"{actual_count}."
        )

    pass_msg(
        f"{priority}: {actual_count}"
    )


# =============================================================================
# OUTPUT SIZE VALIDATION
# =============================================================================

section("OUTPUT SIZE VALIDATION")

text_size = os.path.getsize(
    TEXT_REPORT_FILE
)

json_size = os.path.getsize(
    JSON_REPORT_FILE
)


print(
    f"Text report size : "
    f"{text_size:,} bytes"
)

print(
    f"JSON report size : "
    f"{json_size:,} bytes"
)


if text_size < 1000:
    fail(
        "Text report appears unexpectedly small."
    )

if json_size < 1000:
    fail(
        "JSON report appears unexpectedly small."
    )


pass_msg(
    "Generated report files have valid size."
)


# =============================================================================
# FINAL ANALYTICAL SAFETY SUMMARY
# =============================================================================

section("FINAL ANALYTICAL SAFETY SUMMARY")

print(
    "Comparator available              : NO"
)
print(
    "ROR calculated                    : NO"
)
print(
    "PRR calculated                    : NO"
)
print(
    "Frequency interpreted as incidence: NO"
)
print(
    "Causality established             : NO"
)
print(
    "Disproportionality established    : NO"
)
print(
    "Confirmed safety signal           : NO"
)
print(
    "Confirmed drug interaction        : NO"
)


# =============================================================================
# FINAL RESULT
# =============================================================================

section("FINAL RESULT")

print("PASS")

print()

print(
    "Phase 10 controlled pharmacovigilance "
    "report generation is structurally valid."
)

print()

print("Validated Phase 10 outputs:")
print(
    "- phase10_genai_context.json"
)
print(
    "- phase10_candidate_context.json"
)
print(
    "- phase10_reporting_rules.json"
)
print(
    "- phase10_pharmacovigilance_report.txt"
)
print(
    "- phase10_generated_report.json"
)

print()

print("Phase status:")
print(
    "Phase 1  - Drug normalization        : COMPLETE"
)
print(
    "Phase 2  - Reaction normalization    : COMPLETE"
)
print(
    "Phase 3  - Structure validation      : COMPLETE"
)
print(
    "Phase 4  - Case integration          : COMPLETE"
)
print(
    "Phase 5  - Pharmacovigilance screen  : COMPLETE"
)
print(
    "Phase 6  - Signal pattern analysis   : COMPLETE"
)
print(
    "Phase 7  - Evidence & reporting      : COMPLETE"
)
print(
    "Phase 8  - Structured reporting      : COMPLETE"
)
print(
    "Phase 9  - Decision support          : COMPLETE"
)
print(
    "Phase 10 - Controlled reporting      : COMPLETE"
)

print()

print("IMPORTANT:")
print(
    "No internal non-Bisoprolol comparator exists."
)
print(
    "ROR/PRR have not been calculated."
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
    "Candidate reactions are not confirmed "
    "safety signals."
)
print(
    "Co-medication patterns do not establish "
    "drug-drug interactions."
)
print(
    "Review priorities are triage categories only."
)

print()

print(
    "All Phase 10 analytical safeguards "
    "remain active."
)

print("=" * 100)