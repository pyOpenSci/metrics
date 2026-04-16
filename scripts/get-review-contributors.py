"""Script that grabs, collates and stores review contributor data from our peer review  yaml files.


GOAL: Create a csv file that stores contributor data over time only for editors and reviiewers.


Open yaml file
1. https://github.com/pyOpenSci/pyopensci.github.io/blob/main/_data/contributors.yml
2. Scan contributor_type for editor and or reviewer and populate bool field in spreadsheet accordingly
3. Get location if available and populate

Create an output csv called review_contribs.csv
"""

import os

import pandas as pd
from pydantic import ValidationError

from pyosmeta.file_io import open_yml_file
from pyosmeta.models import PersonModel

# NOTE: the code below is from here https://github.com/pyOpenSci/pyosMeta/blob/main/src/pyosmeta/cli/update_contributors.py
# Consider turning those into functionsor some sort of helper obj so they can be reused here
BASE_URL = "https://raw.githubusercontent.com/pyOpenSci/"
WEB_YAML_PATH = BASE_URL + "pyopensci.github.io/main/_data/contributors.yml"
OUTPUT_PATH = os.path.join("_data", "review_contribs.csv")


def fetch_contributor_data():
    """Fetch and parse contributor data from the YAML file."""
    web_contribs = open_yml_file(WEB_YAML_PATH)

    all_contribs = {}
    for a_contrib in web_contribs:
        try:
            all_contribs[a_contrib["github_username"].lower()] = PersonModel(
                **a_contrib
            )
        except ValidationError as ve:
            print(f"Validation error for {a_contrib['github_username']}: {ve}")

    return all_contribs


def process_contributors(all_contribs):
    """Extract relevant contributor data and return a DataFrame."""
    contrib_data = []
    for name, data in all_contribs.items():
        print(f"Processing: {name}")
        entry = {
            "name": name,
            "location": data.location,
            "date_added": data.date_added,
            "packages_reviewed": len(data.packages_reviewed),
            "packages_eic": len(data.packages_eic),
            "packages_editor": len(data.packages_editor),
            "editor": data.editorial_board,  # Boolean
            "maintainer": any(
                role in data.contributor_type
                for role in ["maintainer", "package-maintainer"]
            ),
        }
        contrib_data.append(entry)

    return pd.DataFrame(contrib_data)


def main():
    """Main function to fetch, process, and save contributor data."""
    print("Fetching contributor data...")
    all_contribs = fetch_contributor_data()

    print("Processing contributors...")
    contrib_df = process_contributors(all_contribs)

    print(f"Saving output to {OUTPUT_PATH}...")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)  # Ensure directory exists
    contrib_df.to_csv(OUTPUT_PATH, index=False)

    print("Done! Contributor data successfully saved.")


# Run as a script
if __name__ == "__main__":
    main()
