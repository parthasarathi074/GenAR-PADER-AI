import pandas as pd

from .schema import REQUIRED_COLUMNS


def validate_required_columns(
    dataframe: pd.DataFrame,
) -> list[str]:
    """
    Check whether all required columns exist.

    Returns
    -------
    list[str]
        Missing required columns.
    """

    actual_columns = set(dataframe.columns)

    missing_columns = sorted(
        REQUIRED_COLUMNS - actual_columns
    )

    return missing_columns


def validate_case_ids(
    dataframe: pd.DataFrame,
) -> dict:
    """
    Validate safety report IDs.
    """

    column = "safetyreportid"

    if column not in dataframe.columns:
        return {
            "valid": False,
            "message": "safetyreportid column is missing.",
        }

    missing_ids = int(
        dataframe[column].isna().sum()
    )

    unique_cases = int(
        dataframe[column].nunique()
    )

    total_rows = len(dataframe)

    return {
        "valid": missing_ids == 0,
        "total_rows": total_rows,
        "unique_cases": unique_cases,
        "missing_case_ids": missing_ids,
    }


def validate_seriousness(
    dataframe: pd.DataFrame,
) -> dict:
    """
    Inspect values present in the serious column.
    """

    column = "serious"

    if column not in dataframe.columns:
        return {
            "valid": False,
            "message": "serious column is missing.",
        }

    values = (
        dataframe[column]
        .dropna()
        .astype(str)
        .str.strip()
        .str.lower()
        .unique()
        .tolist()
    )

    return {
        "valid": len(values) > 0,
        "values_found": sorted(values),
    }


def validate_dataset(
    dataframe: pd.DataFrame,
) -> dict:
    """
    Run all currently implemented validation checks.
    """

    missing_columns = validate_required_columns(
        dataframe
    )

    case_validation = validate_case_ids(
        dataframe
    )

    seriousness_validation = validate_seriousness(
        dataframe
    )

    return {
        "required_columns": {
            "valid": len(missing_columns) == 0,
            "missing": missing_columns,
        },
        "case_ids": case_validation,
        "seriousness": seriousness_validation,
    }