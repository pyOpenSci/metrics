"""Update editorial team CSVs from website board YAML + local domain data.

1. Membership comes from pyopensci.github.io YAML:
   * ``editorial-board.yml`` — active editors (from GitHub teams)
   * ``emeritus-editors.yml`` — emeritus editors (from GitHub teams)
   * ``manual-editorial-roster.yml`` — some editors don't join our org. so to
      list them we need to manually add them to the roster. We use a single file in
      th pyopensci website repository to keep track of this as it's only a few people
      as of 2026 sept 3 total 2 emeritus and 1 acting editor that haven't joined our org and
      thus aren't on our teams.
    This manually generated file is merged with the other two files, merged
     with the same rules as pyosMeta ``merge_manual_roster`` (generated
     YAML wins if the username is already listed)
"""

from pathlib import Path

import pandas as pd
from pyosmeta.constants import WEBSITE_DATA_RAW_URL
from pyosmeta.file_io import open_yml_file

DATA_DIR = Path("data")
EDITOR_PROFILES_PATH = DATA_DIR / "editor_profiles.csv"
EDITORIAL_BOARD_URL = f"{WEBSITE_DATA_RAW_URL}editorial-board.yml"
EMERITUS_EDITORS_URL = f"{WEBSITE_DATA_RAW_URL}emeritus-editors.yml"
MANUAL_ROSTER_URL = f"{WEBSITE_DATA_RAW_URL}manual-editorial-roster.yml"

# True-only flags, same mapping as pyosMeta merge_manual_roster.
_ACTIVE_MANUAL_FLAGS = ("editor", "eic", "peer_review_lead", "triage")
_EMERITUS_MANUAL_FLAGS = (
    "emeritus_editor",
    "emeritus_eic",
    "emeritus_peer_review_lead",
    "emeritus_triage",
)

PROFILE_COLUMNS = [
    "gh_username",
    "first_name",
    "last_name",
    "country",
    "state",
    "OS",
    "Domain_areas",
    "Description",
    "technical_areas",
]


def usernames_from_board_yml(url: str) -> set[str]:
    """Return lowercase GitHub usernames from a board YAML mapping."""
    data = open_yml_file(url)
    if not data:
        raise ValueError(f"Board YAML at {url} is empty or missing")
    return {(u or "").strip().lower() for u in data.keys() if u}


def apply_manual_roster(
    editors: set[str],
    emeritus: set[str],
    manual: dict | None,
) -> tuple[set[str], set[str]]:
    """Add people from the manual roster who are not already listed.

    Board YAML wins if the username is already present — same rule as
    pyosMeta ``merge_manual_roster``. Active flags win over emeritus.
    """
    if not manual:
        return set(editors), set(emeritus)

    editors = set(editors)
    emeritus = set(emeritus)
    for raw_name, flags in manual.items():
        username = (raw_name or "").strip().lower()
        if not username or username in editors or username in emeritus:
            continue
        if not isinstance(flags, dict):
            continue
        if any(flags.get(key) is True for key in _ACTIVE_MANUAL_FLAGS):
            editors.add(username)
        elif any(flags.get(key) is True for key in _EMERITUS_MANUAL_FLAGS):
            emeritus.add(username)
    return editors, emeritus


def load_editor_profiles() -> pd.DataFrame:
    """Load and validate manually maintained editor profile metadata."""
    profiles = pd.read_csv(EDITOR_PROFILES_PATH)
    missing_columns = set(PROFILE_COLUMNS) - set(profiles.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing columns in {EDITOR_PROFILES_PATH}: {missing}")

    profiles = profiles[PROFILE_COLUMNS]
    if profiles["gh_username"].isna().any():
        raise ValueError(f"Blank username in {EDITOR_PROFILES_PATH}")
    profiles["gh_username"] = (
        profiles["gh_username"].astype(str).str.strip().str.lower()
    )
    if profiles["gh_username"].eq("").any():
        raise ValueError(f"Blank username in {EDITOR_PROFILES_PATH}")
    duplicate_usernames = profiles.loc[
        profiles["gh_username"].duplicated(), "gh_username"
    ].tolist()
    if duplicate_usernames:
        duplicates = ", ".join(sorted(duplicate_usernames))
        raise ValueError(f"Duplicate usernames in {EDITOR_PROFILES_PATH}: {duplicates}")
    return profiles


def build_editor_table(
    usernames: set[str], profiles: pd.DataFrame, *, active: bool
) -> pd.DataFrame:
    """Join a roster to stable profile metadata."""
    roster = pd.DataFrame(sorted(usernames), columns=["gh_username"])
    table = roster.merge(profiles, on="gh_username", how="left", indicator=True)
    missing_profiles = table.loc[table["_merge"] == "left_only", "gh_username"].tolist()
    if missing_profiles:
        print("Missing editor profiles:", ", ".join(missing_profiles))

    table = table.drop(columns="_merge")
    table.insert(1, "active", active)
    return table


def main() -> None:
    from_board = usernames_from_board_yml(EDITORIAL_BOARD_URL)
    from_emeritus = usernames_from_board_yml(EMERITUS_EDITORS_URL) - from_board
    manual = open_yml_file(MANUAL_ROSTER_URL) or {}
    if not isinstance(manual, dict):
        manual = {}

    editors, emeritus = apply_manual_roster(from_board, from_emeritus, manual)
    added_active = sorted(editors - from_board)
    added_emeritus = sorted(emeritus - from_emeritus)
    if added_active:
        print("Added from manual roster (active):", ", ".join(added_active))
    if added_emeritus:
        print("Added from manual roster (emeritus):", ", ".join(added_emeritus))

    editor_profiles = load_editor_profiles()
    all_editors = build_editor_table(editors, editor_profiles, active=True)
    all_emeritus = build_editor_table(emeritus, editor_profiles, active=False)

    editors_out = DATA_DIR / "editorial_team_domains.csv"
    emeritus_out = DATA_DIR / "emeritus_editor_domains.csv"
    all_editors.to_csv(editors_out, index=False)
    all_emeritus.to_csv(emeritus_out, index=False)

    print(f"Wrote {len(all_editors)} current editors to {editors_out}")
    print(f"Wrote {len(all_emeritus)} emeritus editors to {emeritus_out}")


if __name__ == "__main__":
    main()
