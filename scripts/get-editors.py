"""This script updates our editorial team csv file with the most current editors.

1. It parses a manually created list of editors found in the csv 
file: `_data/editorial_team_domains`. This csv was created by 
manually adding editor names to the file with domain areas from our Google sheet. 
The (private) google sheet is generated from a google form that collects editor 
expertise and domains when they apply to be an editor with us.
2. The script, uses the GitHub API to return the list of GitHub  usernames from 
the editorial team on GitHub. (see)
  * https://github.com/orgs/pyOpenSci/teams/emeritus-editors/members
  * https://github.com/orgs/pyOpenSci/teams/editorial-board/members
When we onboard a new editor, we add them to the editorial-board GitHub team so 
they have proper permissions in repositories in our organization. When an editor
wishes to step down, we move them to the emeritus-editors team. However, they 
may still be active in reviews so we keep them on the editorial-board team until 
they have completed all of their reviews.

The GitHub team data are collected using the GitHub graphQL interface.

3. Finally, this script merges the data parsed from the team with the .csv file.  

This script creates two .csv files. The _data/editorial_team_domains.csv contains 
all currently "activate" editors. _data/emeritus_editor_domains.csv contains 
editors that are either fully offboarded of intend to offboard after theyr currently 
active reviews. 

TODO:
* it would be good to find a more automated way to get the domain data from our 
Google Sheet. one way to do this would be to create a new spreadsheet that 
pulls from our editor signup but only contains gh username and then the domain 
areas. 

"""

import os

import requests
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path

load_dotenv()

# Replace with your GitHub personal access token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = "https://api.github.com/graphql"


def get_team_members(team_name: str = "editorial-board"):
    """A function that hits the GH graphQL api and pulls down members 
    from our editorial team. This list should be the most current list of 
    pyOpenSci editors. """

    query = """
    query ($slug: String!){
      organization(login: "pyOpenSci") {
        team(slug: $slug) {
          members(first: 100) {
            nodes { login }
          }
        }
      }
    }
    """

    variables = {"slug": team_name}

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.post(
        GITHUB_API_URL, 
        json={"query": query, "variables": variables}, 
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        members = data["data"]["organization"]["team"]["members"]["nodes"]
        return [member["login"] for member in members]
    else:
        print(f"Failed to retrieve team members: {response.status_code}")
        print(response.text)
        return []


def filter_members(members, exclude):
    return [member for member in members if member not in exclude]


if __name__ == "__main__":
    
    # Pull down the list of GitHub usernames from our teams
    editors = get_team_members("editorial-board")
    emeritus = get_team_members("emeritus-editors") 

    # Cleanup usernames
    editors = sorted({(u or "").strip().lower() for u in editors})
    emeritus = sorted({(u or "").strip().lower() for u in emeritus})

    # Open the CSV that contains domain info for editors
    data_dir = Path("_data")
    editor_domains = pd.read_csv(data_dir / "editorial_team_domains.csv")
    editor_domains["gh_username"] = (editor_domains["gh_username"].astype(str))

    # Build DataFrames of current editors and emeritus from the live team lists
    editors_df = pd.DataFrame(editors, columns=["gh_username"]) if editors else pd.DataFrame(columns=["gh_username"]) 
    emeritus_df = pd.DataFrame(emeritus, columns=["gh_username"]) if emeritus else pd.DataFrame(columns=["gh_username"]) 

    # Merge with domain info (left join to keep the team list as the source of truth)
    all_editors = editors_df.merge(editor_domains, on="gh_username", how="left")
    all_emeritus = emeritus_df.merge(editor_domains, on="gh_username", how="left")

    # In the emeritus file, mark all rows as inactive
    all_emeritus["active"] = False

    # Export both CSVs with the same structure
    editors_out = data_dir / "editorial_team_domains.csv"
    emeritus_out = data_dir / "emeritus_editor_domains.csv"

    all_editors.to_csv(editors_out, index=False)
    all_emeritus.to_csv(emeritus_out, index=False)

    # Optional console summary
    print(f"Wrote {len(all_editors)} current editors to {editors_out}")
    print(f"Wrote {len(all_emeritus)} emeritus editors to {emeritus_out}")
