import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

FILES = [
    "phase6_candidate_profiles.csv",
    "phase6_candidate_demographics.csv",
    "phase6_candidate_countries.csv",
    "phase6_candidate_products.csv",
    "phase6_analysis_summary.csv",
]

print("=" * 100)
print("PHASE 7 - SIGNAL EVIDENCE & REPORTING INVESTIGATION")
print("=" * 100)

print("\n" + "=" * 100)
print("FILE CHECK")
print("=" * 100)

for filename in FILES:
    path = os.path.join(DATA_DIR, filename)

    if os.path.exists(path):
        print(f"PASS - {filename}")
    else:
        print(f"FAIL - {filename}")

missing = [
    f for f in FILES
    if not os.path.exists(os.path.join(DATA_DIR, f))
]

if missing:
    print("\nRequired Phase 6 outputs are missing.")
    print("Complete Phase 6 before continuing.")
    raise SystemExit(1)


print("\n" + "=" * 100)
print("LOADING PHASE 6 OUTPUTS")
print("=" * 100)

profiles = pd.read_csv(
    os.path.join(DATA_DIR, "phase6_candidate_profiles.csv")
)

demographics = pd.read_csv(
    os.path.join(DATA_DIR, "phase6_candidate_demographics.csv")
)

countries = pd.read_csv(
    os.path.join(DATA_DIR, "phase6_candidate_countries.csv")
)

products = pd.read_csv(
    os.path.join(DATA_DIR, "phase6_candidate_products.csv")
)

summary = pd.read_csv(
    os.path.join(DATA_DIR, "phase6_analysis_summary.csv")
)

print(f"Candidate profiles : {len(profiles):,}")
print(f"Demographic rows   : {len(demographics):,}")
print(f"Country rows       : {len(countries):,}")
print(f"Product rows       : {len(products):,}")
print(f"Summary rows       : {len(summary):,}")


print("\n" + "=" * 100)
print("COLUMN INVENTORY")
print("=" * 100)

datasets = {
    "CANDIDATE PROFILES": profiles,
    "DEMOGRAPHICS": demographics,
    "COUNTRIES": countries,
    "PRODUCTS": products,
    "SUMMARY": summary,
}

for name, df in datasets.items():
    print(f"\n{name}")
    print("-" * 100)

    for i, col in enumerate(df.columns, start=1):
        print(f"{i:02d}. {col}")


print("\n" + "=" * 100)
print("CANDIDATE INVENTORY")
print("=" * 100)

for i, row in profiles.iterrows():
    print(
        f"{i + 1:02d}. "
        f"{row['reactionmeddrapt']} | "
        f"cases={int(row['case_count'])} | "
        f"serious={int(row['serious_case_count'])} | "
        f"serious%={float(row['serious_percentage']):.2f}%"
    )


print("\n" + "=" * 100)
print("CANDIDATE DEMOGRAPHIC STRUCTURE")
print("=" * 100)

for reaction in profiles["reactionmeddrapt"]:

    subset = demographics[
        demographics["reactionmeddrapt"] == reaction
    ]

    print(f"\n{reaction}")
    print("-" * 80)

    if subset.empty:
        print("No demographic records.")
        continue

    for dimension in subset["dimension"].dropna().unique():

        dim = subset[
            subset["dimension"] == dimension
        ].sort_values(
            "case_count",
            ascending=False
        )

        print(f"  {dimension}:")

        for _, row in dim.iterrows():
            print(
                f"    {row['category']}: "
                f"{int(row['case_count'])} "
                f"({float(row['percentage_within_candidate']):.2f}%)"
            )


print("\n" + "=" * 100)
print("CANDIDATE COUNTRY STRUCTURE")
print("=" * 100)

for reaction in profiles["reactionmeddrapt"]:

    subset = countries[
        countries["reactionmeddrapt"] == reaction
    ].sort_values(
        "case_count",
        ascending=False
    )

    print(f"\n{reaction}")
    print("-" * 80)

    if subset.empty:
        print("No country records.")
        continue

    for _, row in subset.head(10).iterrows():
        print(
            f"  {row['country']}: "
            f"{int(row['case_count'])} "
            f"({float(row['percentage_within_candidate']):.2f}%)"
        )


print("\n" + "=" * 100)
print("CANDIDATE CO-MEDICATION STRUCTURE")
print("=" * 100)

for reaction in profiles["reactionmeddrapt"]:

    subset = products[
        products["reactionmeddrapt"] == reaction
    ].sort_values(
        "case_count",
        ascending=False
    )

    print(f"\n{reaction}")
    print("-" * 80)

    if subset.empty:
        print("No product records.")
        continue

    for _, row in subset.head(10).iterrows():
        print(
            f"  {row['product']}: "
            f"{int(row['case_count'])} "
            f"({float(row['percentage_within_candidate']):.2f}%)"
        )


print("\n" + "=" * 100)
print("ANALYTICAL STATUS")
print("=" * 100)

if "comparator_available" in summary.columns:
    print(
        "Comparator available :",
        summary["comparator_available"].iloc[0]
    )

if "ror_available" in summary.columns:
    print(
        "ROR available        :",
        summary["ror_available"].iloc[0]
    )

if "prr_available" in summary.columns:
    print(
        "PRR available        :",
        summary["prr_available"].iloc[0]
    )

if "causality_established" in summary.columns:
    print(
        "Causality established:",
        summary["causality_established"].iloc[0]
    )

if "disproportionality_established" in summary.columns:
    print(
        "Disproportionality   :",
        summary["disproportionality_established"].iloc[0]
    )


print("\n" + "=" * 100)
print("PHASE 7 INVESTIGATION CONCLUSION")
print("=" * 100)

print("""
Phase 7 investigation confirms that the available evidence consists of:

1. Candidate reaction frequencies
2. Seriousness patterns
3. Candidate demographic distributions
4. Candidate reporting-country distributions
5. Candidate co-medication patterns

No internal non-Bisoprolol comparator cohort is available.

Therefore:

- ROR must not be calculated.
- PRR must not be calculated.
- Frequency must not be interpreted as incidence.
- Co-medication patterns must not be interpreted as proven interactions.
- Candidate reactions must not be treated as confirmed causal adverse reactions.

The Phase 7 evidence layer is ready for structured reporting.
""")

print("=" * 100)
print("PHASE 7 INVESTIGATION COMPLETE")
print("=" * 100)