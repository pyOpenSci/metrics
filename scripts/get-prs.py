"""A script that parses all active pyOS repos and collects contributor and
activity information in the form of opened issues and pull requests.

This script returns a `.csv` file that contains all issue and pr data for items:

* not created by a bot
* and OPENED in the requested year (default: the current year). Items opened
  in an earlier year and updated/closed this year are excluded. Each
  row records ``date_opened`` and ``date_closed`` (empty while still open).

Re-running the script for a previous year (``--year 2024``) rebuilds that
year's file so ``date_closed`` / ``current_status`` pick up items that were
closed later.

The one issue with this workflow is that if it doesn't run on the last day of
the year, then it won't capture the last pr's that might happen on new years
eve week.

This will allow us to track contribution growth overtime.

Ideally this should be run as a cron job, a workflow dispatch and then
on near years eve

    # Run specifically on New Year's Eve at 11:30 PM
    - cron: '30 23 31 12 *'

That way we are sure to capture data for the entirety of 2024 on new years eve!!xw
"""

import argparse
import logging
import os
import time
from datetime import datetime

import pandas as pd
from pyosmeta.github_api import GitHubAPI

logging.basicConfig(level=logging.INFO)


def parse_gh_date(value: str | None) -> datetime | None:
    """Parse a GitHub ISO-8601 timestamp; return None if missing."""
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")


def get_repo_data(
    github_api,
    repo_name,
    endpoint_type,
    contrib_types,
    user_location_cache: dict[str:str],
    start: datetime,
    end: datetime,
):
    """
    Get repository data from GitHub API and save it as a CSV file.

    Parameters
    ----------
    github_api : GitHubAPI
        An instance of the GitHubAPI class.
    repo_name : str
        The name of the repository.
    endpoint_type : str
        The type of endpoint to retrieve data from. Options (pull or issue)
    contrib_types : dict
        A dictionary containing contributor types.
    start, end : datetime
        Only keep items with ``start <= created_at < end``. The GitHub
        ``since`` query filters on *updated_at* (and the pulls endpoint
        ignores it entirely), so the created-date filter must happen here.

    Returns
    -------
    DataFrame
        A pandas DataFrame containing the repository data.

    Raises
    ------
    None
    """

    github_api.endpoint_type = endpoint_type
    items = github_api._get_response_rest(github_api.api_endpoint)
    contrib_type = "contributor"

    data = []
    for item in items:
        # The issues endpoint also returns PRs; those are collected via pulls
        if endpoint_type == "issues" and "pull_request" in item:
            continue

        created_at = parse_gh_date(item["created_at"])
        if not (start <= created_at < end):
            continue  # Opened outside the requested year

        gh_user = item["user"]["login"]
        if gh_user in contrib_types["bots"]:
            continue  # Skip items created by bots
        elif gh_user in contrib_types["pyos_staff"]:
            contrib_type = "staff"
        else:
            contrib_type = "contributor"

        closed_at = parse_gh_date(item.get("closed_at"))
        labels = [label["name"] for label in item.get("labels", [])]

        # TODO: make this a small function
        if gh_user in user_location_cache:
            location = user_location_cache[gh_user]
        else:
            location = github_api.get_user_info(gh_handle=gh_user).get("location", "")
            user_location_cache[gh_user] = location
        data.append(
            {
                "title": item["title"],
                "item_opened_by": created_at,
                "date_opened": created_at,
                "date_closed": closed_at,
                "current_status": item["state"],
                "labels": ", ".join(labels),
                "created_by": gh_user,
                "location": location,
                "contrib_type": contrib_type,
                "repo": repo_name,
                "type": endpoint_type,
            }
        )

    return pd.DataFrame(data)


def process_repo(
    github_api, repo_name, contrib_types, user_location_cache, start, end
):
    """Process a GitHub repository.

    Export a repo_name.csv file for the repo when done.

    Parameters
    ----------
    github_api : object
        The GitHub API object.
    repo_name : str
        The name of the repository to process.
    contrib_types : dict
        A dict containing sublists of pyOS staff members & then bots
        that contribute to pyos repos.
    user_location_cache : dict
        A dictionary containing the cached user locations.
    start, end : datetime
        Only keep items opened in ``[start, end)``.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the processed issues and pull requests of the repository.

    Raises
    ------
    Exception
        If an error occurs during the processing.
    """

    github_api.repo = repo_name
    try:
        print(f" -- Getting issues for {repo_name}")
        issues_df = get_repo_data(
            github_api,
            repo_name,
            "issues",
            contrib_types,
            user_location_cache,
            start,
            end,
        )
        print(f" -- Getting prs for {repo_name}")
        prs_df = get_repo_data(
            github_api,
            repo_name,
            "pulls",
            contrib_types,
            user_location_cache,
            start,
            end,
        )
        print(f" -- Combining issues and prs for {repo_name}")
        all_contribs_df = pd.concat([issues_df, prs_df], ignore_index=True)
        print(f" -- Finished with {repo_name} API calls")

        return all_contribs_df
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return pd.DataFrame()


# First year of pyOpenSci activity; the historical file covers 2018-2023
HISTORICAL_START = 2018
HISTORICAL_END = 2024


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--year",
        type=int,
        default=datetime.now().year,
        help="Collect items opened in this year (default: current year).",
    )
    group.add_argument(
        "--historical",
        action="store_true",
        help=f"Rebuild the {HISTORICAL_START}_{HISTORICAL_END - 1} file.",
    )
    return parser.parse_args()


def main():
    """This workflow
    1. gets the requested year (default: current year).
    2. processes all prs and issues OPENED during that year
    3. creates a data frame with the issues:
       * opened date and closed date (empty if still open)
       * opened by gh handle
       * whether it was opened by staff or a non staff contributor
       * what repo it was opened in
       * whether it's a pr or an issue
       Here are the df headers
       title,item_opened_by,date_opened,date_closed,current_status,labels,created_by,location,contrib_type,repo,type
    It then saves a csv file with data for that year
    """
    print(f"I am working here {os.getcwd()}")

    args = parse_args()
    if args.historical:
        start_year, end_year = HISTORICAL_START, HISTORICAL_END
        csv_name = f"{HISTORICAL_START}_{HISTORICAL_END - 1}_all_issues_prs.csv"
    else:
        start_year, end_year = args.year, args.year + 1
        csv_name = f"{args.year}_all_issues_prs.csv"
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 1, 1)
    print(f"Collecting issues and prs opened in [{start_year}, {end_year})")

    # `since` filters on updated_at, so this only narrows the download;
    # the created_at filter is applied in get_repo_data
    after_date = start.strftime("%Y-%m-%d")

    github_api = GitHubAPI(
        org="pyopensci", repo="", endpoint_type="", after_date=after_date
    )

    contrib_types = {
        "pyos_staff": [
            "lwasser",
            "kierisi",
        ],
        "bots": [
            "allcontributors[bot]",
            "pre-commit-ci[bot]",
        ],
    }

    # Note: this should be stored somewhere centrally as we use this list
    # for the get contributors workflow as well.
    repo_names = [
        "python-package-guide",
        "software-peer-review",
        "pyosMeta",
        "pyopensci.github.io",
        "handbook",
        "software-submission",
        "peer-review-metrics",
        "pyosPackage",
        "pyos-sphinx-theme",
    ]
    all_contribs_final = []

    # Object to reduce user api calls
    user_location_cache = {}
    for repo_name in repo_names:
        start_time = time.time()
        print(f"Processing repository: {repo_name}")
        all_contribs_df = process_repo(
            github_api, repo_name, contrib_types, user_location_cache, start, end
        )

        print(f"Adding data for {repo_name}")

        all_contribs_final.append(all_contribs_df)
        end_time = time.time()

        print(f"{repo_name}--Processing Time: {end_time - start_time:.4f} seconds")

    all_contribs_final_df = pd.concat(all_contribs_final, ignore_index=True)

    # Export to csv
    os.makedirs("data", exist_ok=True)
    csv_path = os.path.join("data", csv_name)
    all_contribs_final_df.to_csv(csv_path, index=False)
    print(f"Saved csv here: {csv_path}")


if __name__ == "__main__":
    main()
