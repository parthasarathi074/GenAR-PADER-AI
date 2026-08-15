from pathlib import Path
import pandas as pd
import re

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
INPUT = DATA / "Bisoprolol_icsr_sample_1068rows.xlsx"


REACTION_FIELDS = [
    "patient_reaction_reactionmeddraversionpt",
    "patient_reaction_reactionmeddrapt",
    "patient_reaction_reactionoutcome",
]


def clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def split_values(value):
    value = clean(value)

    if not value:
        return []

    return [
        item.strip()
        for item in value.split(",")
    ]


def latest_versions(df):

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
        subset=[
            "safetyreportid",
            "safetyreportversion"
        ]
    )

    work = (
        work
        .sort_values(
            [
                "safetyreportid",
                "safetyreportversion"
            ]
        )
        .drop_duplicates(
            "safetyreportid",
            keep="last"
        )
        .reset_index(drop=True)
    )

    return work


def inspect_case(row):

    case_id = int(row["safetyreportid"])
    version = int(row["safetyreportversion"])

    print()
    print("=" * 100)
    print(f"CASE ID: {case_id}")
    print(f"SAFETY VERSION: {version}")
    print("=" * 100)

    values = {}

    for field in REACTION_FIELDS:

        values[field] = split_values(row[field])

        print()
        print(field)
        print("-" * 100)

        print(
            f"Count: {len(values[field])}"
        )

        print(
            f"Raw: {clean(row[field])}"
        )

        for i, value in enumerate(values[field]):

            print(
                f"  [{i}] {value}"
            )

    counts = {
        field: len(values[field])
        for field in REACTION_FIELDS
    }

    print()
    print("REACTION FIELD COUNTS")
    print("-" * 100)

    for field, count in counts.items():
        print(
            f"{field}: {count}"
        )

    max_count = max(
        counts.values(),
        default=0
    )

    mismatched = [
        field
        for field, count in counts.items()
        if count != max_count
    ]

    print()

    if mismatched:

        print(
            "ALIGNMENT WARNING"
        )

        print(
            "The reaction fields do not all have "
            "the same number of values."
        )

        print(
            "Missing positions must remain NULL "
            "rather than shifting later reactions."
        )

    else:

        print(
            "ALIGNMENT OK"
        )


def main():

    print("=" * 100)
    print("PHASE 2 - REACTION STRUCTURE INVESTIGATION")
    print("=" * 100)

    print()
    print("Loading dataset...")
    print(f"Path: {INPUT}")

    df = pd.read_excel(
        INPUT,
        engine="openpyxl"
    )

    print(
        f"Raw rows : {len(df)}"
    )

    print(
        f"Columns  : {len(df.columns)}"
    )

    print()
    print("Checking required reaction columns...")

    missing = [
        field
        for field in REACTION_FIELDS
        if field not in df.columns
    ]

    if missing:

        print(
            "ERROR - Missing reaction columns:"
        )

        for field in missing:
            print(
                f"  {field}"
            )

        return 1

    print(
        "PASS - All reaction columns exist."
    )

    latest = latest_versions(df)

    print()
    print("=" * 100)
    print("LATEST VERSION DATASET")
    print("=" * 100)

    print(
        f"Latest rows   : {len(latest)}"
    )

    print(
        f"Unique cases  : "
        f"{latest['safetyreportid'].nunique()}"
    )

    print()
    print("=" * 100)
    print("REACTION RECORD STATISTICS")
    print("=" * 100)

    statistics = {}

    for field in REACTION_FIELDS:

        counts = latest[field].apply(
            lambda value: len(
                split_values(value)
            )
        )

        statistics[field] = counts

        print()
        print(field)

        print(
            f"  Cases with values : "
            f"{(counts > 0).sum()}"
        )

        print(
            f"  Minimum count     : "
            f"{counts.min()}"
        )

        print(
            f"  Maximum count     : "
            f"{counts.max()}"
        )

        print(
            f"  Average count     : "
            f"{counts.mean():.2f}"
        )

    # Find cases with mismatched reaction field lengths
    mismatch_cases = []

    for _, row in latest.iterrows():

        counts = [
            len(split_values(row[field]))
            for field in REACTION_FIELDS
        ]

        nonzero = [
            count
            for count in counts
            if count > 0
        ]

        if nonzero and len(set(nonzero)) > 1:

            mismatch_cases.append(
                int(row["safetyreportid"])
            )

    print()
    print("=" * 100)
    print("ALIGNMENT SUMMARY")
    print("=" * 100)

    print(
        f"Cases with reaction-field mismatches : "
        f"{len(mismatch_cases)}"
    )

    if mismatch_cases:

        print()
        print("First 10 mismatch cases:")

        for case_id in mismatch_cases[:10]:
            print(
                f"  {case_id}"
            )

    # Inspect representative cases
    print()
    print("=" * 100)
    print("REPRESENTATIVE CASES")
    print("=" * 100)

    selected = []

    # Case with largest reaction count
    reaction_counts = latest[
        "patient_reaction_reactionmeddrapt"
    ].apply(
        lambda value: len(
            split_values(value)
        )
    )

    if len(reaction_counts):

        max_index = reaction_counts.idxmax()

        selected.append(
            max_index
        )

    # First mismatch
    if mismatch_cases:

        mismatch_id = mismatch_cases[0]

        match = latest.index[
            latest["safetyreportid"] == mismatch_id
        ]

        if len(match):

            selected.append(
                match[0]
            )

    # First normal case
    for idx, row in latest.iterrows():

        count = len(
            split_values(
                row[
                    "patient_reaction_reactionmeddrapt"
                ]
            )
        )

        if count > 0:

            selected.append(idx)
            break

    selected = list(
        dict.fromkeys(selected)
    )

    for idx in selected[:3]:

        inspect_case(
            latest.loc[idx]
        )

    print()
    print("=" * 100)
    print("PHASE 2 REACTION STRUCTURE INVESTIGATION COMPLETE")
    print("=" * 100)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )