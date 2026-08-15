from pathlib import Path

import pandas as pd


def load_excel(file_path: str | Path) -> pd.DataFrame:
    """
    Load an Excel safety dataset into a pandas DataFrame.

    Parameters
    ----------
    file_path:
        Path to the Excel file.

    Returns
    -------
    pandas.DataFrame
        Loaded safety data.

    Raises
    ------
    FileNotFoundError
        If the supplied file does not exist.
    ValueError
        If the file is not an Excel file.
    """

    path = Path(file_path)

    # Check that the file exists
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset file not found: {path}"
        )

    # Check that the path is actually a file
    if not path.is_file():
        raise ValueError(
            f"Dataset path is not a file: {path}"
        )

    # Check the file extension
    if path.suffix.lower() not in {".xlsx", ".xls"}:
        raise ValueError(
            "Unsupported file format. "
            "Expected .xlsx or .xls"
        )

    # Load Excel file
    dataframe = pd.read_excel(path)

    return dataframe