import pandas as pd


def select_latest_versions(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Select the latest safety report version
    for every unique safetyreportid.

    The highest safetyreportversion is treated
    as the latest available version.
    """

    required_columns = {
        "safetyreportid",
        "safetyreportversion",
    }

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    working_df = dataframe.copy()

    # Make sure version is numeric
    working_df["safetyreportversion"] = pd.to_numeric(
        working_df["safetyreportversion"],
        errors="coerce",
    )

    # Sort by case ID and version
    working_df = working_df.sort_values(
        by=[
            "safetyreportid",
            "safetyreportversion",
        ],
        ascending=[
            True,
            True,
        ],
    )

    # Keep the highest version for each case
    latest_df = (
        working_df
        .drop_duplicates(
            subset=["safetyreportid"],
            keep="last",
        )
        .reset_index(drop=True)
    )

    return latest_df