import os
import sys
import json
from datetime import datetime


# =============================================================================
# PHASE 10 - CONTROLLED PHARMACOVIGILANCE REPORT GENERATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

CONTEXT_FILE = os.path.join(
    DATA_DIR,
    "phase10_genai_context.json"
)

CANDIDATE_CONTEXT_FILE = os.path.join(
    DATA_DIR,
    "phase10_candidate_context.json"
)

RULES_FILE = os.path.join(
    DATA_DIR,
    "phase10_reporting_rules.json"
)

OUTPUT_REPORT = os.path.join(
    DATA_DIR,
    "phase10_pharmacovigilance_report.txt"
)

OUTPUT_JSON = os.path.join(
    DATA_DIR,
    "phase10_generated_report.json"
)


# =============================================================================
# HELPERS
# =============================================================================

def header(title):
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


def section(title):
    print()
    print("=" * 100)
    print(title)
    print("-" * 100)


def fail(message):
    print(f"FAIL - {message}")
    raise SystemExit(1)


def pass_msg(message):
    print(f"PASS - {message}")


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        fail(
            f"Unable to load {os.path.basename(path)}: {exc}"
        )


def safe_text(value):
    if value is None:
        return ""
    return str(value).strip()


def format_priority(priority):
    mapping = {
        "higher_priority_candidate": "Higher priority",
        "moderate_priority_candidate": "Moderate priority",
        "lower_priority_candidate": "Lower priority",
    }

    return mapping.get(
        safe_text(priority),
        safe_text(priority).replace("_", " ").title()
    )


def write_section(lines, title):
    lines.append("")
    lines.append(title)
    lines.append("=" * len(title))
    lines.append("")


# =============================================================================
# START
# =============================================================================

header(
    "PHASE 10 - CONTROLLED PHARMACOVIGILANCE REPORT GENERATION"
)


# =============================================================================
# FILE CHECK
# =============================================================================

section("FILE CHECK")

required_files = [
    CONTEXT_FILE,
    CANDIDATE_CONTEXT_FILE,
    RULES_FILE,
]

for path in required_files:

    if not os.path.exists(path):
        fail(
            f"Required file missing: "
            f"{os.path.basename(path)}"
        )

    if os.path.getsize(path) == 0:
        fail(
            f"Required file is empty: "
            f"{os.path.basename(path)}"
        )

    pass_msg(
        os.path.basename(path)
    )


# =============================================================================
# LOAD CONTROLLED CONTEXT
# =============================================================================

section("LOADING CONTROLLED GENAI CONTEXT")

context = load_json(
    CONTEXT_FILE
)

candidate_file = load_json(
    CANDIDATE_CONTEXT_FILE
)

rules = load_json(
    RULES_FILE
)

dataset = context.get(
    "dataset_summary",
    {}
)

safety = context.get(
    "analytical_safety",
    {}
)

candidates = context.get(
    "candidates",
    []
)

limitations = context.get(
    "analytical_limitations",
    []
)


print(
    f"Context version       : "
    f"{context.get('context_version')}"
)

print(
    f"Integrated cases      : "
    f"{dataset.get('integrated_cases', 0):,}"
)

print(
    f"Bisoprolol cases      : "
    f"{dataset.get('bisoprolol_cases', 0):,}"
)

print(
    f"Candidate reactions   : "
    f"{len(candidates)}"
)

print(
    f"Analytical limitations: "
    f"{len(limitations)}"
)


# =============================================================================
# CONTEXT CONSISTENCY
# =============================================================================

section("CONTEXT CONSISTENCY VALIDATION")

candidate_file_candidates = candidate_file.get(
    "candidates",
    []
)

if len(candidates) != 8:
    fail(
        f"Expected 8 candidates in master context; "
        f"found {len(candidates)}."
    )

if len(candidate_file_candidates) != 8:
    fail(
        f"Expected 8 candidates in candidate context; "
        f"found {len(candidate_file_candidates)}."
    )

master_names = {
    item["reaction"]
    for item in candidates
}

candidate_names = {
    item["reaction"]
    for item in candidate_file_candidates
}

if master_names != candidate_names:
    fail(
        "Candidate context does not match master context."
    )

pass_msg(
    "Master and candidate contexts are consistent."
)


# =============================================================================
# ANALYTICAL SAFETY GATE
# =============================================================================

section("ANALYTICAL SAFETY GATE")

prohibited_true_flags = [
    "comparator_available",
    "ror_available",
    "prr_available",
    "frequency_is_incidence",
    "causality_established",
    "disproportionality_established",
    "confirmed_signal_established",
    "drug_interaction_established",
]

for flag in prohibited_true_flags:

    value = safety.get(flag)

    print(
        f"{flag:<40}: {value}"
    )

    if value is not False:
        fail(
            f"Unsafe or unexpected analytical state: "
            f"{flag}={value}"
        )

pass_msg(
    "Analytical safety restrictions confirmed."
)


# =============================================================================
# CANDIDATE SAFETY VALIDATION
# =============================================================================

section("CANDIDATE SAFETY VALIDATION")

candidate_prohibited_flags = [
    "confirmed_signal",
    "confirmed_adverse_reaction",
    "causality_established",
    "disproportionality_established",
    "incidence_established",
    "interaction_established",
]

for candidate in candidates:

    reaction = candidate.get(
        "reaction",
        "[UNKNOWN]"
    )

    for flag in candidate_prohibited_flags:

        value = candidate.get(flag)

        if value is not False:
            fail(
                f"Unsafe candidate state: "
                f"{reaction} -> {flag}={value}"
            )

pass_msg(
    "No candidate contains prohibited conclusions."
)


# =============================================================================
# BUILD REPORT
# =============================================================================

section("BUILDING CONTROLLED REPORT")

report_lines = []

report_lines.append(
    "GENAR-PADER-AI"
)

report_lines.append(
    "PHARMACOVIGILANCE DECISION-SUPPORT REPORT"
)

report_lines.append(
    "=" * 80
)

report_lines.append("")

report_lines.append(
    "Analysis scope: Bisoprolol-containing safety reports"
)

report_lines.append(
    "Analysis type: Descriptive and exploratory pharmacovigilance review"
)

report_lines.append(
    "Report generation layer: Controlled structured-data reporting"
)


# =============================================================================
# 1. EXECUTIVE SUMMARY
# =============================================================================

write_section(
    report_lines,
    "1. EXECUTIVE SUMMARY"
)

report_lines.append(
    f"The analysis contains "
    f"{dataset.get('integrated_cases', 0):,} integrated safety reports. "
    f"All {dataset.get('bisoprolol_cases', 0):,} cases contain "
    f"Bisoprolol exposure."
)

report_lines.append("")

report_lines.append(
    f"A total of {dataset.get('candidate_reactions', 0)} "
    f"reaction candidates met the exploratory screening "
    f"criteria and were retained for review prioritization."
)

report_lines.append("")

report_lines.append(
    f"The review-priority distribution consists of "
    f"{dataset.get('higher_priority_candidates', 0)} higher-priority, "
    f"{dataset.get('moderate_priority_candidates', 0)} moderate-priority, "
    f"and {dataset.get('lower_priority_candidates', 0)} "
    f"lower-priority candidates."
)

report_lines.append("")

report_lines.append(
    f"The highest-ranked review candidate is "
    f"{dataset.get('top_candidate', 'Unknown')}, with "
    f"{dataset.get('top_candidate_cases', 0)} reported cases."
)

report_lines.append("")

report_lines.append(
    "These classifications represent review-priority categories only. "
    "They do not represent confirmed pharmacovigilance signals."
)


# =============================================================================
# 2. DATASET OVERVIEW
# =============================================================================

write_section(
    report_lines,
    "2. DATASET OVERVIEW"
)

report_lines.append(
    f"Integrated safety reports: "
    f"{dataset.get('integrated_cases', 0):,}"
)

report_lines.append(
    f"Bisoprolol-containing reports: "
    f"{dataset.get('bisoprolol_cases', 0):,}"
)

report_lines.append(
    f"Candidate reactions: "
    f"{dataset.get('candidate_reactions', 0)}"
)

report_lines.append(
    f"Higher-priority candidates: "
    f"{dataset.get('higher_priority_candidates', 0)}"
)

report_lines.append(
    f"Moderate-priority candidates: "
    f"{dataset.get('moderate_priority_candidates', 0)}"
)

report_lines.append(
    f"Lower-priority candidates: "
    f"{dataset.get('lower_priority_candidates', 0)}"
)


# =============================================================================
# 3. METHODOLOGY
# =============================================================================

write_section(
    report_lines,
    "3. METHODOLOGY OVERVIEW"
)

report_lines.append(
    "Candidate reactions were identified in the preceding validated "
    "pharmacovigilance analysis phases and classified for review "
    "priority using reported-case frequency and seriousness patterns."
)

report_lines.append("")

report_lines.append(
    "The current reporting stage does not perform new primary "
    "pharmacovigilance calculations. It converts validated structured "
    "results into a human-readable decision-support report."
)

report_lines.append("")

report_lines.append(
    "No internal non-Bisoprolol comparator cohort is available. "
    "Therefore ROR and PRR are not calculated and no "
    "disproportionality conclusion is made."
)


# =============================================================================
# 4. PRIORITY SUMMARY
# =============================================================================

write_section(
    report_lines,
    "4. CANDIDATE REVIEW PRIORITY SUMMARY"
)

sorted_candidates = sorted(
    candidates,
    key=lambda item: item.get("rank", 999)
)

for candidate in sorted_candidates:

    report_lines.append(
        f"{candidate['rank']:02d}. "
        f"{candidate['reaction']} | "
        f"Reported cases: {candidate['reported_cases']} | "
        f"Serious cases: {candidate['serious_cases']} | "
        f"Priority: {format_priority(candidate['review_priority'])}"
    )


# =============================================================================
# 5. CANDIDATE EVIDENCE
# =============================================================================

write_section(
    report_lines,
    "5. CANDIDATE-BY-CANDIDATE EVIDENCE"
)

for candidate in sorted_candidates:

    reaction = candidate["reaction"]

    report_lines.append(
        f"5.{candidate['rank']} {reaction}"
    )

    report_lines.append(
        "-" * (
            len(reaction) + 4 +
            len(str(candidate["rank"]))
        )
    )

    report_lines.append(
        f"Reported cases: "
        f"{candidate['reported_cases']}"
    )

    report_lines.append(
        f"Percentage of analyzed cases: "
        f"{candidate['percentage_of_all_cases']:.2f}%"
    )

    report_lines.append(
        f"Serious cases: "
        f"{candidate['serious_cases']} "
        f"({candidate['serious_percentage']:.2f}%)"
    )

    report_lines.append(
        f"Death cases: "
        f"{candidate['death_cases']}"
    )

    report_lines.append(
        f"Hospitalization cases: "
        f"{candidate['hospitalization_cases']}"
    )

    report_lines.append(
        f"Review priority: "
        f"{format_priority(candidate['review_priority'])}"
    )

    report_lines.append("")

    report_lines.append(
        "Evidence summary:"
    )

    report_lines.append(
        candidate["evidence_summary"]
    )

    report_lines.append("")

    report_lines.append(
        "Recommended follow-up:"
    )

    report_lines.append(
        candidate["follow_up_recommendation"]
    )

    report_lines.append("")

    report_lines.append(
        "Interpretation:"
    )

    report_lines.append(
        "This reaction represents a reported-case review candidate. "
        "Causality, incidence, disproportionality, and confirmed "
        "signal status are not established."
    )

    report_lines.append("")


# =============================================================================
# 6. SERIOUSNESS
# =============================================================================

write_section(
    report_lines,
    "6. SERIOUSNESS ASSESSMENT"
)

for candidate in sorted_candidates:

    report_lines.append(
        f"{candidate['reaction']}: "
        f"{candidate['serious_cases']} serious cases "
        f"out of {candidate['reported_cases']} reported cases "
        f"({candidate['serious_percentage']:.2f}%). "
        f"Deaths={candidate['death_cases']}; "
        f"hospitalizations={candidate['hospitalization_cases']}."
    )

report_lines.append("")

report_lines.append(
    "Seriousness information describes the characteristics of "
    "reported cases and must not be interpreted as an estimate "
    "of population-level risk."
)


# =============================================================================
# 7. FOLLOW-UP ACTIONS
# =============================================================================

write_section(
    report_lines,
    "7. RECOMMENDED FOLLOW-UP ACTIONS"
)

for candidate in sorted_candidates:

    report_lines.append(
        f"{candidate['reaction']} "
        f"({format_priority(candidate['review_priority'])}):"
    )

    report_lines.append(
        candidate["recommended_action"]
    )

    report_lines.append("")


# =============================================================================
# 8. LIMITATIONS
# =============================================================================

write_section(
    report_lines,
    "8. ANALYTICAL LIMITATIONS"
)

for limitation in limitations:

    report_lines.append(
        f"Limitation {limitation['limitation_id']}: "
        f"{limitation['limitation']}"
    )

    report_lines.append(
        f"Impact: {limitation['impact']}"
    )

    report_lines.append(
        f"Restriction: {limitation['restriction']}"
    )

    report_lines.append("")


# =============================================================================
# 9. INTERPRETATION BOUNDARIES
# =============================================================================

write_section(
    report_lines,
    "9. INTERPRETATION BOUNDARIES"
)

boundaries = [
    "Reported frequencies are not incidence estimates.",
    "No causal relationship between Bisoprolol and the candidate reactions is established.",
    "No internal non-Bisoprolol comparator cohort is available.",
    "ROR has not been calculated.",
    "PRR has not been calculated.",
    "No disproportionality conclusion is established.",
    "Candidate reactions are not confirmed safety signals.",
    "Candidate reactions are not confirmed adverse reactions.",
    "Co-medication patterns do not establish drug-drug interactions.",
    "Review-priority classifications are triage categories only.",
]

for boundary in boundaries:
    report_lines.append(
        f"- {boundary}"
    )


# =============================================================================
# 10. FINAL SUMMARY
# =============================================================================

write_section(
    report_lines,
    "10. FINAL PHARMACOVIGILANCE SUMMARY"
)

report_lines.append(
    f"The analysis identified "
    f"{dataset.get('candidate_reactions', 0)} candidate reactions "
    f"for structured review among "
    f"{dataset.get('integrated_cases', 0):,} Bisoprolol-containing "
    f"safety reports."
)

report_lines.append("")

report_lines.append(
    f"{dataset.get('top_candidate', 'The highest-ranked candidate')} "
    f"received the highest review priority, with "
    f"{dataset.get('top_candidate_cases', 0)} reported cases."
)

report_lines.append("")

report_lines.append(
    "The candidate ranking is intended to support pharmacovigilance "
    "case-review prioritization and hypothesis generation."
)

report_lines.append("")

report_lines.append(
    "The available dataset does not support incidence estimation, "
    "causal attribution, disproportionality analysis, confirmation "
    "of a safety signal, or confirmation of drug-drug interactions."
)

report_lines.append("")

report_lines.append(
    "Further assessment should incorporate detailed case-level "
    "clinical review, temporal relationships, dechallenge/rechallenge "
    "information where available, alternative etiologies, "
    "co-medications, underlying disease, product information, "
    "and appropriate external evidence."
)


# =============================================================================
# WRITE TEXT REPORT
# =============================================================================

section("WRITING TEXT REPORT")

report_text = "\n".join(
    report_lines
)

with open(
    OUTPUT_REPORT,
    "w",
    encoding="utf-8"
) as file:
    file.write(report_text)

pass_msg(
    "phase10_pharmacovigilance_report.txt created."
)


# =============================================================================
# BUILD MACHINE-READABLE REPORT
# =============================================================================

section("BUILDING MACHINE-READABLE REPORT")

machine_report = {
    "report_version": "phase10_report_v1",

    "project": "GenAR-PADER-AI",

    "report_type":
        "controlled_pharmacovigilance_decision_support",

    "dataset_summary":
        dataset,

    "candidate_count":
        len(sorted_candidates),

    "candidates":
        sorted_candidates,

    "limitations":
        limitations,

    "analytical_safety":
        safety,

    "reporting_rules":
        rules,

    "final_interpretation": {
        "frequency_is_incidence": False,
        "causality_established": False,
        "disproportionality_established": False,
        "confirmed_signal_established": False,
        "drug_interaction_established": False,
        "ror_available": False,
        "prr_available": False,
    },
}


with open(
    OUTPUT_JSON,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        machine_report,
        file,
        indent=2,
        ensure_ascii=False
    )

pass_msg(
    "phase10_generated_report.json created."
)


# =============================================================================
# REPORT VALIDATION
# =============================================================================

section("REPORT SAFETY VALIDATION")

lower_report = report_text.lower()

prohibited_phrases = [
    "confirmed causal relationship",
    "confirmed safety signal was established",
    "bisoprolol causes",
    "incidence rate is",
    "ror demonstrates",
    "prr demonstrates",
    "confirmed drug-drug interaction",
]

for phrase in prohibited_phrases:

    if phrase in lower_report:
        fail(
            f"Unsafe report phrase detected: "
            f"{phrase}"
        )

pass_msg(
    "No prohibited interpretation detected."
)


# =============================================================================
# NUMERICAL CONSISTENCY
# =============================================================================

section("NUMERICAL CONSISTENCY VALIDATION")

for candidate in sorted_candidates:

    reaction = candidate["reaction"]

    if reaction not in report_text:
        fail(
            f"Candidate missing from report: "
            f"{reaction}"
        )

pass_msg(
    "All candidate reactions are represented."
)

if str(
    dataset["integrated_cases"]
) not in report_text.replace(",", ""):
    fail(
        "Integrated case count missing from report."
    )

pass_msg(
    "Integrated case count represented."
)


# =============================================================================
# OUTPUT CHECK
# =============================================================================

section("OUTPUT CHECK")

for path in [
    OUTPUT_REPORT,
    OUTPUT_JSON,
]:

    if not os.path.exists(path):
        fail(
            f"Missing output: "
            f"{os.path.basename(path)}"
        )

    if os.path.getsize(path) == 0:
        fail(
            f"Empty output: "
            f"{os.path.basename(path)}"
        )

    pass_msg(
        os.path.basename(path)
    )


# =============================================================================
# REPORT PREVIEW
# =============================================================================

section("REPORT PREVIEW")

print(
    f"Integrated cases : "
    f"{dataset['integrated_cases']:,}"
)

print(
    f"Candidates       : "
    f"{len(sorted_candidates)}"
)

print(
    f"Top candidate    : "
    f"{dataset['top_candidate']}"
)

print(
    f"Top cases        : "
    f"{dataset['top_candidate_cases']}"
)

print()

print("Candidate ranking:")

for candidate in sorted_candidates:

    print(
        f"{candidate['rank']:02d}. "
        f"{candidate['reaction']:<35} "
        f"cases={candidate['reported_cases']:>3} "
        f"priority={candidate['review_priority']}"
    )


# =============================================================================
# FINAL SAFETY STATUS
# =============================================================================

section("FINAL ANALYTICAL SAFETY STATUS")

print(
    "Comparator available             : NO"
)

print(
    "ROR calculated                   : NO"
)

print(
    "PRR calculated                   : NO"
)

print(
    "Frequency interpreted as incidence: NO"
)

print(
    "Causality established            : NO"
)

print(
    "Disproportionality established   : NO"
)

print(
    "Confirmed safety signal          : NO"
)

print(
    "Confirmed drug interaction       : NO"
)


# =============================================================================
# COMPLETE
# =============================================================================

header(
    "PHASE 10 REPORT GENERATION COMPLETE"
)

print(
    "Generated files:"
)

print(
    " - data\\phase10_pharmacovigilance_report.txt"
)

print(
    " - data\\phase10_generated_report.json"
)

print()

print(
    "The controlled pharmacovigilance report "
    "has been generated successfully."
)

print()

print(
    "IMPORTANT:"
)

print(
    "The report is descriptive and exploratory."
)

print(
    "Review priorities are triage categories only."
)

print(
    "No causal, incidence, disproportionality, "
    "confirmed-signal, or interaction conclusion "
    "has been established."
)

print()

print(
    "Next step:"
)

print(
    "validate_phase10.py"
)