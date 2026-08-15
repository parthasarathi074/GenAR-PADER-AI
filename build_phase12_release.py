import os
import json
import hashlib
import shutil
import pandas as pd
from datetime import datetime, timezone


# =============================================================================
# PHASE 12 - FINAL RELEASE PACKAGE BUILDER
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

RELEASE_DIR = os.path.join(
    BASE_DIR,
    "release"
)

RELEASE_DATA_DIR = os.path.join(
    RELEASE_DIR,
    "data"
)


# =============================================================================
# RELEASE FILES
# =============================================================================

RELEASE_SOURCE_FILES = [
    # Core normalized datasets
    "normalized_drugs.csv",
    "normalized_reactions.csv",
    "integrated_icsr_cases.csv",

    # Alignment / quality reports
    "drug_alignment_report.csv",
    "reaction_alignment_report.csv",

    # Final Phase 9 outputs
    "phase9_signal_assessment.csv",
    "phase9_candidate_summaries.csv",
    "phase9_safety_assessment.csv",
    "phase9_limitation_assessment.csv",
    "phase9_decision_support.csv",
    "phase9_analysis_summary.csv",

    # Phase 10 reporting layer
    "phase10_genai_context.json",
    "phase10_candidate_context.json",
    "phase10_reporting_rules.json",
    "phase10_pharmacovigilance_report.txt",
    "phase10_generated_report.json",

    # Phase 11 application layer
    "phase11_dashboard_summary.json",
    "phase11_candidate_table.csv",
    "phase11_candidate_cards.json",
    "phase11_application_metadata.json",
    "phase11_api_payload.json",
]


MANIFEST_FILE = os.path.join(
    RELEASE_DIR,
    "phase12_release_manifest.json"
)

SUMMARY_FILE = os.path.join(
    RELEASE_DIR,
    "phase12_release_summary.json"
)

README_FILE = os.path.join(
    RELEASE_DIR,
    "RELEASE_README.txt"
)

CHECKSUM_FILE = os.path.join(
    RELEASE_DIR,
    "phase12_checksums.sha256"
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
    raise SystemExit(1)


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        fail(
            f"Unable to load {os.path.basename(path)}: {exc}"
        )


def write_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False
            )
    except Exception as exc:
        fail(
            f"Unable to write {os.path.basename(path)}: {exc}"
        )


def sha256_file(path):
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        while True:
            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


# =============================================================================
# START
# =============================================================================

section(
    "PHASE 12 - FINAL RELEASE PACKAGE BUILD"
)


# =============================================================================
# SOURCE FILE VALIDATION
# =============================================================================

section("SOURCE FILE VALIDATION")

for filename in RELEASE_SOURCE_FILES:

    path = os.path.join(
        DATA_DIR,
        filename
    )

    if not os.path.exists(path):
        fail(
            f"Required release source missing: {filename}"
        )

    if os.path.getsize(path) == 0:
        fail(
            f"Required release source empty: {filename}"
        )

    pass_msg(filename)


# =============================================================================
# LOAD FINAL APPLICATION STATE
# =============================================================================

section("LOADING FINAL APPLICATION STATE")

dashboard = load_json(
    os.path.join(
        DATA_DIR,
        "phase11_dashboard_summary.json"
    )
)

metadata = load_json(
    os.path.join(
        DATA_DIR,
        "phase11_application_metadata.json"
    )
)

api_payload = load_json(
    os.path.join(
        DATA_DIR,
        "phase11_api_payload.json"
    )
)

candidate_table = pd.read_csv(
    os.path.join(
        DATA_DIR,
        "phase11_candidate_table.csv"
    )
)

drugs = pd.read_csv(
    os.path.join(
        DATA_DIR,
        "normalized_drugs.csv"
    )
)

reactions = pd.read_csv(
    os.path.join(
        DATA_DIR,
        "normalized_reactions.csv"
    )
)

integrated = pd.read_csv(
    os.path.join(
        DATA_DIR,
        "integrated_icsr_cases.csv"
    )
)


print(
    f"Normalized drugs     : {len(drugs):,}"
)

print(
    f"Normalized reactions : {len(reactions):,}"
)

print(
    f"Integrated cases     : {len(integrated):,}"
)

print(
    f"Candidate reactions  : {len(candidate_table)}"
)


# =============================================================================
# FINAL COUNT SAFETY GATE
# =============================================================================

section("FINAL COUNT VALIDATION")

if len(drugs) != 10444:
    fail(
        f"Unexpected drug count: {len(drugs):,}"
    )

pass_msg(
    "Drug records = 10,444"
)


if len(reactions) != 3423:
    fail(
        f"Unexpected reaction count: {len(reactions):,}"
    )

pass_msg(
    "Reaction records = 3,423"
)


if len(integrated) != 1024:
    fail(
        f"Unexpected integrated case count: {len(integrated):,}"
    )

pass_msg(
    "Integrated cases = 1,024"
)


if len(candidate_table) != 8:
    fail(
        f"Unexpected candidate count: {len(candidate_table)}"
    )

pass_msg(
    "Candidate reactions = 8"
)


# =============================================================================
# FINAL ANALYTICAL SAFETY GATE
# =============================================================================

section("FINAL ANALYTICAL SAFETY GATE")

restrictions = metadata.get(
    "analytical_restrictions",
    {}
)


required_false_flags = [
    "comparator_available",
    "ror_available",
    "prr_available",
    "frequency_is_incidence",
    "causality_established",
    "disproportionality_established",
    "confirmed_signal_established",
    "drug_interaction_established",
]


for flag in required_false_flags:

    if flag not in restrictions:
        fail(
            f"Missing analytical restriction: {flag}"
        )

    value = restrictions[flag]

    print(
        f"{flag:<40}: {value}"
    )

    if value is not False:
        fail(
            f"Unsafe analytical release state: "
            f"{flag}={value}"
        )


pass_msg(
    "Final analytical safety restrictions preserved."
)


# =============================================================================
# FINAL FRONTEND SAFETY GATE
# =============================================================================

section("FINAL FRONTEND SAFETY GATE")

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

    if display.get(flag) is not False:
        fail(
            f"Unsafe frontend release state: {flag}"
        )

    print(
        f"{flag:<35}: False"
    )


pass_msg(
    "Unsafe analytical frontend options remain disabled."
)


# =============================================================================
# RELEASE DIRECTORY
# =============================================================================

section("PREPARING RELEASE DIRECTORY")

if os.path.exists(RELEASE_DIR):
    shutil.rmtree(RELEASE_DIR)

os.makedirs(
    RELEASE_DATA_DIR,
    exist_ok=True
)

pass_msg(
    f"Release directory created: {RELEASE_DIR}"
)


# =============================================================================
# COPY RELEASE DATA
# =============================================================================

section("COPYING RELEASE FILES")

copied_files = []


for filename in RELEASE_SOURCE_FILES:

    source = os.path.join(
        DATA_DIR,
        filename
    )

    destination = os.path.join(
        RELEASE_DATA_DIR,
        filename
    )

    shutil.copy2(
        source,
        destination
    )

    copied_files.append(
        destination
    )

    print(
        f"COPY - {filename}"
    )


pass_msg(
    f"{len(copied_files)} release data files copied."
)


# =============================================================================
# BUILD FILE MANIFEST
# =============================================================================

section("BUILDING RELEASE MANIFEST")

manifest_files = []


for path in copied_files:

    filename = os.path.basename(path)

    manifest_files.append(
        {
            "filename":
                filename,

            "relative_path":
                os.path.join(
                    "data",
                    filename
                ).replace("\\", "/"),

            "size_bytes":
                os.path.getsize(path),

            "sha256":
                sha256_file(path),
        }
    )


release_manifest = {
    "project":
        "GenAR-PADER-AI",

    "release_version":
        "1.0.0",

    "pipeline_version":
        "12-phase validated pipeline",

    "release_status":
        "validated_release_candidate",

    "release_file_count":
        len(manifest_files),

    "files":
        manifest_files,

    "data_integrity": {
        "normalized_drug_records":
            len(drugs),

        "normalized_reaction_records":
            len(reactions),

        "integrated_cases":
            len(integrated),

        "candidate_reactions":
            len(candidate_table),
    },

    "top_candidate": {
        "reaction":
            dashboard[
                "top_candidate"
            ][
                "reaction"
            ],

        "reported_cases":
            dashboard[
                "top_candidate"
            ][
                "reported_cases"
            ],

        "priority":
            dashboard[
                "top_candidate"
            ][
                "priority"
            ],
    },

    "analytical_restrictions": {
        "comparator_available": False,
        "ror_available": False,
        "prr_available": False,
        "frequency_is_incidence": False,
        "causality_established": False,
        "disproportionality_established": False,
        "confirmed_signal_established": False,
        "drug_interaction_established": False,
    },

    "release_scope":
        "Descriptive and exploratory pharmacovigilance "
        "decision-support application.",

    "release_generated_utc":
        datetime.now(
            timezone.utc
        ).isoformat(),
}


write_json(
    MANIFEST_FILE,
    release_manifest
)

pass_msg(
    "Release manifest created."
)


# =============================================================================
# BUILD RELEASE SUMMARY
# =============================================================================

section("BUILDING RELEASE SUMMARY")

priority_distribution = dashboard.get(
    "priority_distribution",
    {}
)


release_summary = {
    "project_name":
        "GenAR-PADER-AI",

    "release_version":
        "1.0.0",

    "phase_status": {
        "phase_1": "complete",
        "phase_2": "complete",
        "phase_3": "complete",
        "phase_4": "complete",
        "phase_5": "complete",
        "phase_6": "complete",
        "phase_7": "complete",
        "phase_8": "complete",
        "phase_9": "complete",
        "phase_10": "complete",
        "phase_11": "complete",
        "phase_12": "release_build_complete",
    },

    "pipeline_summary": {
        "drug_records":
            10444,

        "reaction_records":
            3423,

        "integrated_cases":
            1024,

        "candidate_reactions":
            8,
    },

    "priority_distribution": {
        "higher":
            priority_distribution.get(
                "higher_priority_candidate",
                0
            ),

        "moderate":
            priority_distribution.get(
                "moderate_priority_candidate",
                0
            ),

        "lower":
            priority_distribution.get(
                "lower_priority_candidate",
                0
            ),
    },

    "top_candidate":
        dashboard.get(
            "top_candidate"
        ),

    "application_outputs": [
        "phase11_dashboard_summary.json",
        "phase11_candidate_table.csv",
        "phase11_candidate_cards.json",
        "phase11_application_metadata.json",
        "phase11_api_payload.json",
    ],

    "human_readable_report":
        "phase10_pharmacovigilance_report.txt",

    "machine_readable_report":
        "phase10_generated_report.json",

    "safety_position": {
        "confirmed_signal": False,
        "incidence_established": False,
        "causality_established": False,
        "disproportionality_established": False,
        "drug_interaction_established": False,
    },

    "release_note":
        "This release provides descriptive and exploratory "
        "pharmacovigilance decision support only.",
}


write_json(
    SUMMARY_FILE,
    release_summary
)

pass_msg(
    "Release summary created."
)


# =============================================================================
# BUILD CHECKSUM FILE
# =============================================================================

section("BUILDING CHECKSUM FILE")

checksum_lines = []


for entry in manifest_files:

    checksum_lines.append(
        f"{entry['sha256']}  "
        f"{entry['relative_path']}"
    )


with open(
    CHECKSUM_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "\n".join(
            checksum_lines
        )
    )

    file.write("\n")


pass_msg(
    "SHA-256 checksum file created."
)


# =============================================================================
# BUILD RELEASE README
# =============================================================================

section("BUILDING RELEASE README")

readme_text = f"""
GenAR-PADER-AI
FINAL VALIDATED RELEASE
================================================================================

Release version
---------------
1.0.0

Pipeline
--------
12-phase pharmacovigilance data and decision-support pipeline.

Core validated counts
----------------------
Normalized drug records     : 10,444
Normalized reaction records : 3,423
Integrated ICSR cases       : 1,024
Candidate reactions         : 8

Candidate priority distribution
--------------------------------
Higher priority   : 1
Moderate priority : 2
Lower priority    : 5

Top review-priority candidate
-----------------------------
Reaction       : Acute kidney injury
Reported cases : 22
Priority       : higher_priority_candidate

Release contents
----------------
data/
    normalized datasets
    integrated dataset
    decision-support outputs
    controlled report outputs
    dashboard/API-ready outputs

phase12_release_manifest.json
    Complete release file manifest with SHA-256 hashes.

phase12_release_summary.json
    Final pipeline and release summary.

phase12_checksums.sha256
    File integrity checksums.

Analytical interpretation
-------------------------
The project performs descriptive and exploratory pharmacovigilance
review prioritization.

IMPORTANT ANALYTICAL RESTRICTIONS
---------------------------------
No internal non-Bisoprolol comparator is available.

ROR was not calculated.
PRR was not calculated.

Reported frequency is not incidence.

Causality is not established.

Disproportionality is not established.

Candidate reactions are not confirmed safety signals.

Co-medication patterns do not establish drug-drug interactions.

Review-priority categories are triage classifications only.

Release status
--------------
RELEASE CANDIDATE

Final Phase 12 validation must pass before the release is considered
fully validated.

================================================================================
"""


with open(
    README_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        readme_text.strip()
        + "\n"
    )


pass_msg(
    "Release README created."
)


# =============================================================================
# RELEASE OUTPUT CHECK
# =============================================================================

section("RELEASE OUTPUT CHECK")

release_control_files = [
    MANIFEST_FILE,
    SUMMARY_FILE,
    README_FILE,
    CHECKSUM_FILE,
]


for path in release_control_files:

    if not os.path.exists(path):
        fail(
            f"Release control file missing: "
            f"{os.path.basename(path)}"
        )

    if os.path.getsize(path) == 0:
        fail(
            f"Release control file empty: "
            f"{os.path.basename(path)}"
        )

    pass_msg(
        os.path.basename(path)
    )


# =============================================================================
# HASH VERIFICATION
# =============================================================================

section("INITIAL HASH VERIFICATION")

for entry in manifest_files:

    path = os.path.join(
        RELEASE_DIR,
        entry[
            "relative_path"
        ]
    )

    actual_hash = sha256_file(
        path
    )

    if actual_hash != entry["sha256"]:
        fail(
            f"Checksum mismatch: "
            f"{entry['filename']}"
        )


pass_msg(
    "All copied release files match manifest SHA-256 hashes."
)


# =============================================================================
# RELEASE SIZE
# =============================================================================

section("RELEASE PACKAGE STATISTICS")

total_data_size = sum(
    entry["size_bytes"]
    for entry in manifest_files
)


print(
    f"Release data files : "
    f"{len(manifest_files)}"
)

print(
    f"Release data size  : "
    f"{total_data_size:,} bytes"
)

print(
    f"Control files      : "
    f"{len(release_control_files)}"
)


# =============================================================================
# FINAL RELEASE SAFETY STATUS
# =============================================================================

section("FINAL RELEASE ANALYTICAL SAFETY")

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
# PHASE 12 BUILD COMPLETE
# =============================================================================

section(
    "PHASE 12 RELEASE BUILD COMPLETE"
)

print(
    "Release directory:"
)

print(
    RELEASE_DIR
)

print()

print(
    "Generated release control files:"
)

print(
    " - phase12_release_manifest.json"
)

print(
    " - phase12_release_summary.json"
)

print(
    " - phase12_checksums.sha256"
)

print(
    " - RELEASE_README.txt"
)

print()

print(
    "Release data directory:"
)

print(
    " - release\\data\\"
)

print()

print(
    "IMPORTANT:"
)

print(
    "This is currently a RELEASE CANDIDATE."
)

print(
    "The next and final step is:"
)

print()

print(
    "validate_phase12.py"
)