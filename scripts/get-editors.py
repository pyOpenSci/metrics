"""Update editorial team CSVs from website board YAML + local domain data.

1. Membership comes from pyopensci.github.io board YAML (written by
   pyosMeta ``update-editorial-board`` from GitHub teams + manual roster):
   * ``data/editorial-board.yml`` — active editors
   * ``data/emeritus-editors.yml`` — emeritus editors
2. Domain / expertise columns come from the local CSV
   ``data/editorial_team_domains.csv`` (curated from the editor signup
   Google Sheet).
3. Merge usernames with domain rows and write:
   * ``data/editorial_team_domains.csv`` — current active editors
   * ``data/emeritus_editor_domains.csv`` — emeritus (``active`` = False)

TODO:
* Automate domain data from the Google Sheet (gh username + domains only).
"""

from pathlib import Path

import pandas as pd
from pyosmeta.constants import WEBSITE_DATA_RAW_URL
from pyosmeta.file_io import open_yml_file

DATA_DIR = Path("data")
EDITORIAL_BOARD_URL = f"{WEBSITE_DATA_RAW_URL}editorial-board.yml"
EMERITUS_EDITORS_URL = f"{WEBSITE_DATA_RAW_URL}emeritus-editors.yml"


def usernames_from_board_yml(url: str) -> list[str]:
    """Return sorted lowercase GitHub usernames from a board YAML mapping."""
    data = open_yml_file(url)
    if not data:
        raise ValueError(f"Board YAML at {url} is empty or missing")
    return sorted({(u or "").strip().lower() for u in data.keys() if u})


def main() -> None:
    editors = usernames_from_board_yml(EDITORIAL_BOARD_URL)
    emeritus = usernames_from_board_yml(EMERITUS_EDITORS_URL)

    editor_domains = pd.read_csv(DATA_DIR / "editorial_team_domains.csv")
    editor_domains["gh_username"] = editor_domains["gh_username"].astype(str)

    editors_df = pd.DataFrame(editors, columns=["gh_username"])
    emeritus_df = pd.DataFrame(emeritus, columns=["gh_username"])

    # Left join: website roster is the membership source of truth
    all_editors = editors_df.merge(editor_domains, on="gh_username", how="left")
    all_emeritus = emeritus_df.merge(
        editor_domains, on="gh_username", how="left"
    )
    all_emeritus["active"] = False

    editors_out = DATA_DIR / "editorial_team_domains.csv"
    emeritus_out = DATA_DIR / "emeritus_editor_domains.csv"
    all_editors.to_csv(editors_out, index=False)
    all_emeritus.to_csv(emeritus_out, index=False)

    print(f"Wrote {len(all_editors)} current editors to {editors_out}")
    print(f"Wrote {len(all_emeritus)} emeritus editors to {emeritus_out}")


if __name__ == "__main__":
    main()
