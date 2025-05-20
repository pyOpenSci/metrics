import os

import github
import pandas as pd
import yaml
from pathlib import Path

ACCESS_TOKEN = os.getenv("GITHUB_TOKEN")
gh = github.Github(ACCESS_TOKEN)

def get_package_data():
    """
    Get package data from GitHub repository.

    Returns
    -------
    dict
        Dictionary containing package data.
    """
    
    # Get the repository
    repo = gh.get_repo("pyOpenSci/pyopensci.github.io")
    
    # Get the ``_data/packages.yml`` file
    package_data = repo.get_contents("_data/packages.yml")
    package_data = package_data.decoded_content.decode("utf-8")
    
    # Load the YAML content
    package_data = yaml.safe_load(package_data)
    
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame.from_dict(package_data)
    
    return df

if __name__ == "__main__":
    package_df = get_package_data()
    
    dir_path = Path("_data")
    file_path = dir_path / "package_data.csv"

    dir_path.mkdir(parents=True, exist_ok=True)
    package_df.to_csv(file_path, index=False)
