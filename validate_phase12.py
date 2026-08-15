import os
import json
import sys
import hashlib
import pandas as pd


# =============================================================================
# PHASE 12 - FINAL RELEASE VALIDATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RELEASE_DIR = os.path.join(
    BASE_DIR,
    "release"
)

RELEASE_DATA_DIR = os.path.join(
    RELEASE_DIR,
    "data"
)

MANIFEST_FILE = os.path.join(
    RELEASE_DIR,
    "phase12_release_manifest.json"
)

SUMMARY_FILE = os.path.join(
    RELEASE_DIR,
    "phase12_release_summary.json"
)

CHECKSUM_FILE = os.path.join(
    RELEASE_DIR,
    "phase12_checksums.sha256"
)

README_FILE = os.path.join(
    RELEASE_DIR,
    "RELEASE_README.txt"
)


# =============================================================================
# EXPECTED RELEASE DATA FILES
# =============================================================================

EXPECTED_RELEASE_FILES = [
    "normalized_drugs.csv",
    "normalized_reactions.csv",
    "integrated_icsr_cases.csv",
    "drug_alignment_report.csv",
    "reaction_alignment_report.csv",

    "phase9_signal_assessment.csv",
    "phase9_candidate_summaries.csv",
    "phase9_safety_assessment.csv",
    "phase9_limitation_assessment.csv",
    "phase9_decision_support.csv",
    "phase9_analysis_summary.csv",

    "phase10_genai_context.json",
    "phase10_candidate_context.json",
    "phase10_reporting_rules.json",
    "phase10_pharmacovigilance_report.txt",
    "phase10_generated_report.json",

    "phase11_dashboard_summary.json",
    "phase11_candidate_table.csv",
    "phase11_candidate_cards.json",
    "phase11_application_metadata.json",
    "phase11_api_payload.json",
]


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
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except Exception as exc:
        fail(
            f"Unable to read "
            f"{os.path.basename(path)}: {exc}"
        )


def load_text(path):
    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:
            return file.read()

    except Exception as exc:
        fail(
            f"Unable to read "
            f"{os.path.basename(path)}: {exc}"
        )


def sha256_file(path):
    digest = hashlib.sha256()

    with open(
        path,
        "rb"
    ) as file:

        while True:
            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(
                chunk
            )

    return digest.hexdigest()


def as_bool(value):

    if isinstance(value, bool):
        return value

    if value is None:
        return None

    text = str(value).strip().lower()

    if text in {
        "true",
        "yes",
        "1"
    }:
        return True

    if text in {
        "false",
        "no",
        "0"
    }:
        return False

    return None


# =============================================================================
# START
# =============================================================================

section(
    "PHASE 12 - FINAL RELEASE VALIDATION"
)


# =============================================================================
# RELEASE DIRECTORY CHECK
# =============================================================================

section(
    "RELEASE DIRECTORY CHECK"
)

if not os.path.exists(
    RELEASE_DIR
):
    fail(
        "Release directory does not exist."
    )

pass_msg(
    f"Release directory exists: "
    f"{RELEASE_DIR}"
)


if not os.path.isdir(
    RELEASE_DATA_DIR
):
    fail(
        "Release data directory does not exist."
    )

pass_msg(
    "Release data directory exists."
)


# =============================================================================
# RELEASE CONTROL FILE CHECK
# =============================================================================

section(
    "RELEASE CONTROL FILE CHECK"
)

control_files = [
    MANIFEST_FILE,
    SUMMARY_FILE,
    CHECKSUM_FILE,
    README_FILE,
]


for path in control_files:

    if not os.path.exists(path):
        fail(
            f"Missing release control file: "
            f"{os.path.basename(path)}"
        )

    if os.path.getsize(path) == 0:
        fail(
            f"Empty release control file: "
            f"{os.path.basename(path)}"
        )

    pass_msg(
        os.path.basename(path)
    )


# =============================================================================
# RELEASE DATA FILE CHECK
# =============================================================================

section(
    "RELEASE DATA FILE CHECK"
)

actual_release_files = sorted(
    [
        name
        for name in os.listdir(
            RELEASE_DATA_DIR
        )
        if os.path.isfile(
            os.path.join(
                RELEASE_DATA_DIR,
                name
            )
        )
    ]
)


if len(actual_release_files) != 21:
    fail(
        f"Expected 21 release data files, "
        f"found {len(actual_release_files)}."
    )

pass_msg(
    "Release data directory contains 21 files."
)


expected_set = set(
    EXPECTED_RELEASE_FILES
)

actual_set = set(
    actual_release_files
)


if expected_set != actual_set:

    missing = sorted(
        expected_set - actual_set
    )

    unexpected = sorted(
        actual_set - expected_set
    )

    if missing:
        print(
            "Missing release files:"
        )

        for filename in missing:
            print(
                f"  - {filename}"
            )

    if unexpected:
        print(
            "Unexpected release files:"
        )

        for filename in unexpected:
            print(
                f"  - {filename}"
            )

    fail(
        "Release data file inventory mismatch."
    )


pass_msg(
    "Release data inventory exactly matches expected files."
)


# =============================================================================
# LOAD MANIFEST
# =============================================================================

section(
    "RELEASE MANIFEST VALIDATION"
)

manifest = load_json(
    MANIFEST_FILE
)


expected_manifest_values = {
    "project":
        "GenAR-PADER-AI",

    "release_version":
        "1.0.0",

    "pipeline_version":
        "12-phase validated pipeline",

    "release_status":
        "validated_release_candidate",

    "release_file_count":
        21,
}


for key, expected in (
    expected_manifest_values.items()
):

    actual = manifest.get(
        key
    )

    if actual != expected:
        fail(
            f"Manifest {key}: "
            f"expected {expected!r}, "
            f"found {actual!r}"
        )

    pass_msg(
        f"{key}: {expected}"
    )


manifest_files = manifest.get(
    "files",
    []
)


if len(manifest_files) != 21:
    fail(
        f"Manifest expected 21 files, "
        f"found {len(manifest_files)}."
    )

pass_msg(
    "Manifest contains 21 file records."
)


# =============================================================================
# MANIFEST FILE STRUCTURE
# =============================================================================

section(
    "MANIFEST FILE STRUCTURE VALIDATION"
)

required_manifest_file_fields = [
    "filename",
    "relative_path",
    "size_bytes",
    "sha256",
]


manifest_filename_set = set()


for index, entry in enumerate(
    manifest_files,
    start=1
):

    for field in (
        required_manifest_file_fields
    ):

        if field not in entry:
            fail(
                f"Manifest entry {index} "
                f"missing field: {field}"
            )

    filename = entry[
        "filename"
    ]

    manifest_filename_set.add(
        filename
    )

    if filename not in expected_set:
        fail(
            f"Unexpected manifest file: "
            f"{filename}"
        )


if manifest_filename_set != expected_set:
    fail(
        "Manifest file names do not match "
        "expected release inventory."
    )


pass_msg(
    "Manifest file structures are valid."
)


# =============================================================================
# SHA-256 HASH VALIDATION
# =============================================================================

section(
    "SHA-256 HASH VALIDATION"
)


for entry in manifest_files:

    relative_path = entry[
        "relative_path"
    ].replace(
        "/",
        os.sep
    )

    path = os.path.join(
        RELEASE_DIR,
        relative_path
    )

    if not os.path.exists(path):
        fail(
            f"Manifest file not found: "
            f"{relative_path}"
        )

    actual_size = os.path.getsize(
        path
    )

    expected_size = entry[
        "size_bytes"
    ]

    if actual_size != expected_size:
        fail(
            f"Size mismatch for "
            f"{entry['filename']}: "
            f"expected {expected_size}, "
            f"found {actual_size}"
        )

    actual_hash = sha256_file(
        path
    )

    expected_hash = entry[
        "sha256"
    ]

    if actual_hash != expected_hash:
        fail(
            f"SHA-256 mismatch: "
            f"{entry['filename']}"
        )

    print(
        f"PASS - "
        f"{entry['filename']}"
    )


pass_msg(
    "All 21 release files passed "
    "SHA-256 integrity validation."
)


# =============================================================================
# CHECKSUM FILE VALIDATION
# =============================================================================

section(
    "CHECKSUM FILE VALIDATION"
)

checksum_text = load_text(
    CHECKSUM_FILE
)

checksum_lines = [
    line.strip()
    for line in checksum_text.splitlines()
    if line.strip()
]


if len(checksum_lines) != 21:
    fail(
        f"Expected 21 checksum lines, "
        f"found {len(checksum_lines)}."
    )

pass_msg(
    "Checksum file contains 21 entries."
)


checksum_lookup = {}


for line in checksum_lines:

    parts = line.split(
        None,
        1
    )

    if len(parts) != 2:
        fail(
            f"Invalid checksum line: {line}"
        )

    sha_value = parts[0].strip()

    relative_path = parts[1].strip()

    checksum_lookup[
        relative_path
    ] = sha_value


for entry in manifest_files:

    relative_path = entry[
        "relative_path"
    ]

    expected_hash = entry[
        "sha256"
    ]

    if relative_path not in checksum_lookup:
        fail(
            f"Checksum entry missing for: "
            f"{relative_path}"
        )

    if (
        checksum_lookup[
            relative_path
        ]
        != expected_hash
    ):
        fail(
            f"Checksum file mismatch for: "
            f"{relative_path}"
        )


pass_msg(
    "Checksum file matches release manifest."
)


# =============================================================================
# CORE DATA VALIDATION
# =============================================================================

section(
    "CORE RELEASE DATA VALIDATION"
)

drugs = pd.read_csv(
    os.path.join(
        RELEASE_DATA_DIR,
        "normalized_drugs.csv"
    )
)

reactions = pd.read_csv(
    os.path.join(
        RELEASE_DATA_DIR,
        "normalized_reactions.csv"
    )
)

integrated = pd.read_csv(
    os.path.join(
        RELEASE_DATA_DIR,
        "integrated_icsr_cases.csv"
    )
)

candidate_table = pd.read_csv(
    os.path.join(
        RELEASE_DATA_DIR,
        "phase11_candidate_table.csv"
    )
)


print(
    f"Drug records      : "
    f"{len(drugs):,}"
)

print(
    f"Reaction records  : "
    f"{len(reactions):,}"
)

print(
    f"Integrated cases  : "
    f"{len(integrated):,}"
)

print(
    f"Candidates        : "
    f"{len(candidate_table)}"
)


if len(drugs) != 10444:
    fail(
        "Normalized drug record count mismatch."
    )

if len(reactions) != 3423:
    fail(
        "Normalized reaction record count mismatch."
    )

if len(integrated) != 1024:
    fail(
        "Integrated case count mismatch."
    )

if len(candidate_table) != 8:
    fail(
        "Candidate count mismatch."
    )


pass_msg(
    "Core release counts are valid."
)


# =============================================================================
# CASE COVERAGE VALIDATION
# =============================================================================

section(
    "CASE COVERAGE VALIDATION"
)

drug_cases = drugs[
    "safetyreportid"
].nunique()

reaction_cases = reactions[
    "safetyreportid"
].nunique()

integrated_cases = integrated[
    "safetyreportid"
].nunique()


print(
    f"Drug cases       : {drug_cases:,}"
)

print(
    f"Reaction cases   : {reaction_cases:,}"
)

print(
    f"Integrated cases : {integrated_cases:,}"
)


if drug_cases != 1024:
    fail(
        "Drug case coverage mismatch."
    )

if reaction_cases != 1024:
    fail(
        "Reaction case coverage mismatch."
    )

if integrated_cases != 1024:
    fail(
        "Integrated case coverage mismatch."
    )


pass_msg(
    "All release datasets represent "
    "1,024 safety cases."
)


# =============================================================================
# DATA INTEGRITY SECTION OF MANIFEST
# =============================================================================

section(
    "MANIFEST DATA INTEGRITY VALIDATION"
)

data_integrity = manifest.get(
    "data_integrity",
    {}
)


expected_data_integrity = {
    "normalized_drug_records":
        10444,

    "normalized_reaction_records":
        3423,

    "integrated_cases":
        1024,

    "candidate_reactions":
        8,
}


for key, expected in (
    expected_data_integrity.items()
):

    actual = data_integrity.get(
        key
    )

    if actual != expected:
        fail(
            f"Manifest data integrity "
            f"{key}: expected {expected}, "
            f"found {actual}"
        )

    pass_msg(
        f"{key}: {expected}"
    )


# =============================================================================
# RELEASE SUMMARY VALIDATION
# =============================================================================

section(
    "RELEASE SUMMARY VALIDATION"
)

summary = load_json(
    SUMMARY_FILE
)


if (
    summary.get(
        "project_name"
    )
    != "GenAR-PADER-AI"
):
    fail(
        "Release summary project name mismatch."
    )

pass_msg(
    "Project name: GenAR-PADER-AI"
)


if (
    summary.get(
        "release_version"
    )
    != "1.0.0"
):
    fail(
        "Release summary version mismatch."
    )

pass_msg(
    "Release version: 1.0.0"
)


pipeline_summary = summary.get(
    "pipeline_summary",
    {}
)


expected_pipeline_summary = {
    "drug_records": 10444,
    "reaction_records": 3423,
    "integrated_cases": 1024,
    "candidate_reactions": 8,
}


for key, expected in (
    expected_pipeline_summary.items()
):

    actual = pipeline_summary.get(
        key
    )

    if actual != expected:
        fail(
            f"Release summary {key} mismatch."
        )

    pass_msg(
        f"{key}: {expected}"
    )


# =============================================================================
# PHASE STATUS VALIDATION
# =============================================================================

section(
    "PHASE STATUS VALIDATION"
)

phase_status = summary.get(
    "phase_status",
    {}
)


for phase in range(
    1,
    12
):

    key = f"phase_{phase}"

    if phase_status.get(
        key
    ) != "complete":

        fail(
            f"{key} is not marked complete."
        )

    pass_msg(
        f"Phase {phase}: COMPLETE"
    )


if (
    phase_status.get(
        "phase_12"
    )
    != "release_build_complete"
):
    fail(
        "Phase 12 release build status invalid."
    )


pass_msg(
    "Phase 12 release build complete."
)


# =============================================================================
# PRIORITY DISTRIBUTION VALIDATION
# =============================================================================

section(
    "PRIORITY DISTRIBUTION VALIDATION"
)

priority = summary.get(
    "priority_distribution",
    {}
)


expected_priority = {
    "higher": 1,
    "moderate": 2,
    "lower": 5,
}


for key, expected in (
    expected_priority.items()
):

    actual = priority.get(
        key
    )

    if actual != expected:
        fail(
            f"Priority count mismatch: "
            f"{key}"
        )

    pass_msg(
        f"{key}: {expected}"
    )


# =============================================================================
# TOP CANDIDATE VALIDATION
# =============================================================================

section(
    "TOP CANDIDATE VALIDATION"
)

top = summary.get(
    "top_candidate",
    {}
)


if (
    top.get(
        "reaction"
    )
    != "Acute kidney injury"
):
    fail(
        "Top candidate mismatch."
    )

pass_msg(
    "Top candidate: Acute kidney injury"
)


if (
    top.get(
        "reported_cases"
    )
    != 22
):
    fail(
        "Top candidate case count mismatch."
    )

pass_msg(
    "Top candidate reported cases: 22"
)


if (
    top.get(
        "priority"
    )
    != "higher_priority_candidate"
):
    fail(
        "Top candidate priority mismatch."
    )

pass_msg(
    "Top candidate priority valid."
)


# =============================================================================
# APPLICATION METADATA VALIDATION
# =============================================================================

section(
    "FINAL APPLICATION METADATA VALIDATION"
)

metadata = load_json(
    os.path.join(
        RELEASE_DATA_DIR,
        "phase11_application_metadata.json"
    )
)

restrictions = metadata.get(
    "analytical_restrictions",
    {}
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

    if flag not in restrictions:
        fail(
            f"Missing analytical safety flag: "
            f"{flag}"
        )

    value = as_bool(
        restrictions[
            flag
        ]
    )

    if value is not False:
        fail(
            f"Final analytical safety violation: "
            f"{flag}={value}"
        )

    pass_msg(
        f"{flag}: False"
    )


# =============================================================================
# API DISPLAY SAFETY
# =============================================================================

section(
    "FINAL API DISPLAY SAFETY"
)

api_payload = load_json(
    os.path.join(
        RELEASE_DATA_DIR,
        "phase11_api_payload.json"
    )
)

display = api_payload.get(
    "display",
    {}
)


unsafe_display_flags = [
    "show_ror",
    "show_prr",
    "show_incidence",
    "show_causality_claim",
    "show_confirmed_signal",
    "show_confirmed_interaction",
]


for flag in unsafe_display_flags:

    value = as_bool(
        display.get(
            flag
        )
    )

    if value is not False:
        fail(
            f"Unsafe API display flag enabled: "
            f"{flag}"
        )

    pass_msg(
        f"{flag}: disabled"
    )


# =============================================================================
# SAFE DISPLAY VALIDATION
# =============================================================================

section(
    "DESCRIPTIVE DISPLAY VALIDATION"
)

allowed_display_flags = [
    "show_reported_frequency",
    "show_seriousness",
    "show_review_priority",
    "show_follow_up_recommendation",
    "show_limitations",
]


for flag in allowed_display_flags:

    value = as_bool(
        display.get(
            flag
        )
    )

    if value is not True:
        fail(
            f"Expected descriptive display "
            f"option not enabled: {flag}"
        )

    pass_msg(
        f"{flag}: enabled"
    )


# =============================================================================
# FINAL REPORT SAFETY LANGUAGE
# =============================================================================

section(
    "FINAL REPORT SAFETY LANGUAGE"
)

report_text = load_text(
    os.path.join(
        RELEASE_DATA_DIR,
        "phase10_pharmacovigilance_report.txt"
    )
)

lower_report = (
    report_text.lower()
)


required_safety_concepts = {
    "incidence restriction": [
        "reported frequencies are not incidence estimates",
        "frequency is not interpreted as incidence",
    ],

    "causality restriction": [
        "causality is not established",
        "no causal relationship",
    ],

    "ROR restriction": [
        "ror has not been calculated",
        "ror was not calculated",
    ],

    "PRR restriction": [
        "prr has not been calculated",
        "prr was not calculated",
    ],

    "signal restriction": [
        "candidate reactions are not confirmed safety signals",
        "no confirmed safety signal",
    ],
}


for concept, alternatives in (
    required_safety_concepts.items()
):

    found = any(
        phrase in lower_report
        for phrase in alternatives
    )

    if not found:
        fail(
            f"Final report missing safety concept: "
            f"{concept}"
        )

    pass_msg(
        concept
    )


# =============================================================================
# RELEASE README VALIDATION
# =============================================================================

section(
    "RELEASE README VALIDATION"
)

readme = load_text(
    README_FILE
)

required_readme_terms = [
    "GenAR-PADER-AI",
    "FINAL VALIDATED RELEASE",
    "10,444",
    "3,423",
    "1,024",
    "Acute kidney injury",
    "RELEASE CANDIDATE",
    "ROR was not calculated",
    "PRR was not calculated",
    "Causality is not established",
]


for term in required_readme_terms:

    if term not in readme:
        fail(
            f"Release README missing: "
            f"{term}"
        )

    pass_msg(
        term
    )


# =============================================================================
# RELEASE PACKAGE SIZE
# =============================================================================

section(
    "RELEASE PACKAGE STATISTICS"
)

release_data_size = 0


for filename in actual_release_files:

    release_data_size += os.path.getsize(
        os.path.join(
            RELEASE_DATA_DIR,
            filename
        )
    )


control_size = sum(
    os.path.getsize(
        path
    )
    for path in control_files
)


print(
    f"Release data files : "
    f"{len(actual_release_files)}"
)

print(
    f"Release data size  : "
    f"{release_data_size:,} bytes"
)

print(
    f"Control files      : "
    f"{len(control_files)}"
)

print(
    f"Control size       : "
    f"{control_size:,} bytes"
)

print(
    f"Total release size : "
    f"{release_data_size + control_size:,} bytes"
)


# =============================================================================
# FINAL ANALYTICAL SAFETY STATUS
# =============================================================================

section(
    "FINAL ANALYTICAL SAFETY STATUS"
)

print(
    "Comparator cohort available          : NO"
)

print(
    "ROR calculated                        : NO"
)

print(
    "PRR calculated                        : NO"
)

print(
    "Frequency interpreted as incidence   : NO"
)

print(
    "Causality established                : NO"
)

print(
    "Disproportionality established       : NO"
)

print(
    "Confirmed safety signal established  : NO"
)

print(
    "Drug-drug interaction established    : NO"
)


# =============================================================================
# FINAL PIPELINE STATUS
# =============================================================================

section(
    "FINAL PIPELINE STATUS"
)

phase_names = {
    1: "Drug normalization",
    2: "Reaction normalization",
    3: "Structure validation",
    4: "Case integration",
    5: "Pharmacovigilance screen",
    6: "Signal pattern analysis",
    7: "Evidence & reporting",
    8: "Structured reporting",
    9: "Decision support",
    10: "Controlled reporting",
    11: "Application output",
    12: "Release validation",
}


for phase in range(
    1,
    13
):

    print(
        f"Phase {phase:<2} - "
        f"{phase_names[phase]:<35}: COMPLETE"
    )


# =============================================================================
# FINAL RESULT
# =============================================================================

section(
    "FINAL RESULT"
)

print(
    "PASS"
)

print()

print(
    "GenAR-PADER-AI final release package "
    "is structurally and analytically valid."
)

print()

print(
    "Release version: 1.0.0"
)

print(
    "Pipeline phases completed: 12 / 12"
)

print(
    "Phases remaining: 0"
)

print()

print(
    "FINAL PROJECT STATUS:"
)

print(
    "COMPLETE"
)

print()

print(
    "Validated release directory:"
)

print(
    RELEASE_DIR
)

print()

print(
    "Validated release contents:"
)

print(
    "- 21 packaged pipeline/application files"
)

print(
    "- phase12_release_manifest.json"
)

print(
    "- phase12_release_summary.json"
)

print(
    "- phase12_checksums.sha256"
)

print(
    "- RELEASE_README.txt"
)

print()

print(
    "All packaged data files passed "
    "SHA-256 integrity verification."
)

print()

print(
    "Analytical interpretation remains "
    "descriptive and exploratory."
)

print(
    "No incidence, causality, "
    "disproportionality, confirmed-signal, "
    "or confirmed-interaction conclusion "
    "has been established."
)

print()

print("=" * 100)