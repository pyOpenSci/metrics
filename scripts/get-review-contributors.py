"""Fetch website contributors.yml and write data/review_contribs.csv.

Keeps editors/reviewers (and related fields) from website YAML via PersonModel.
Does not call the update_contributors CLI (that writes website YAML).
"""

import os
import sys

import pandas as pd
from pydantic import ValidationError
from pyosmeta.constants import CONTRIBUTORS_RAW_URL
from pyosmeta.file_io import open_yml_file
from pyosmeta.models import PersonModel

OUTPUT_PATH = os.path.join("data", "review_contribs.csv")


def fetch_contributor_data() -> dict[str, PersonModel]:
    """Fetch contributors.yml and validate each entry with PersonModel."""
    web_contribs = open_yml_file(CONTRIBUTORS_RAW_URL)
    if not web_contribs:
        raise ValueError(
            f"contributors.yml at {CONTRIBUTORS_RAW_URL} is empty or missing"
        )

    all_contribs = {}
    for a_contrib in web_contribs:
        try:
            all_contribs[a_contrib["github_username"].lower()] = PersonModel(
                **a_contrib
            )
        except ValidationError as ve:
            print(
                f"Validation error for {a_contrib.get('github_username')}: {ve}",
                file=sys.stderr,
            )

    return all_contribs


def process_contributors(all_contribs: dict[str, PersonModel]) -> pd.DataFrame:
    """Extract relevant contributor data and return a DataFrame."""
    contrib_data = []
    for name, data in all_contribs.items():
        entry = {
            "name": name,
            "location": data.location,
            "date_added": data.date_added,
            "packages_reviewed": len(data.packages_reviewed),
            "packages_eic": len(data.packages_eic),
            "packages_editor": len(data.packages_editor),
            "editor": data.editorial_board,
            "maintainer": any(
                role in data.contributor_type
                for role in ["maintainer", "package-maintainer"]
            ),
        }
        contrib_data.append(entry)

    return pd.DataFrame(contrib_data)


def main():
    """Fetch, process, and save contributor data."""
    print("Fetching contributor data...")
    all_contribs = fetch_contributor_data()

    print(f"Processing {len(all_contribs)} contributors...")
    contrib_df = process_contributors(all_contribs)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    contrib_df.to_csv(OUTPUT_PATH, index=False)

    print(f"Wrote {len(contrib_df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
