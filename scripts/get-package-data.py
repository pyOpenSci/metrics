"""Fetch website packages.yml and write data/package_data.csv."""

from pathlib import Path

import pandas as pd
from pyosmeta.constants import PACKAGES_RAW_URL
from pyosmeta.file_io import open_yml_file


def get_package_data() -> pd.DataFrame:
    """Load packages.yml via pyosMeta raw URL and return a DataFrame."""
    package_data = open_yml_file(PACKAGES_RAW_URL)
    if not package_data:
        raise ValueError(f"packages.yml at {PACKAGES_RAW_URL} is empty or missing")
    return pd.DataFrame(package_data)


if __name__ == "__main__":
    package_df = get_package_data()

    dir_path = Path("data")
    file_path = dir_path / "package_data.csv"

    dir_path.mkdir(parents=True, exist_ok=True)
    package_df.to_csv(file_path, index=False)
