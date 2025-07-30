"""This script updates our editorial team csv file with the most current editors.

1. It parses a partially  manually created list of editors found int he csv 
file: `_data/editorial_team_domains`. This csv was initially created by 
manually adding editor names to the file with domain areas from our google sheet. 
The (private) google sheet collects what domains they can support when they 
apply to be an editor
2. It then hits the github api to return the list of gh usernames from the editorial team on GitHub
When we onboard a new editor, we add them to that team so they have proper permissions in repos in our org.
The GitHub team data are grabbed using graphQL.

3. Finally, this script merges the data parsed from the team with the csv file.  

The output is a csv file called _data/editorial_team_domains.csv that can be 
used to parse editor data. 

TODO:
* it would be good to find a more automated way to get the domain data from our 
google sheet. one way to do this would be to create a new spreadsheet that 
pulls from our editor signup but only contains gh username and then the domain areas. 

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


def get_team_members():
    """A function that hits the GH graphQL api and pulled down members 
    from our editorial team. This list should be the most current list of 
    pyOpenSci editors. """

    query = """
    {
      organization(login: "pyOpenSci") {
        team(slug: "editorial-board") {
          members(first: 100) {
            nodes {
              login
            }
          }
        }
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.post(
        GITHUB_API_URL, json={"query": query}, headers=headers
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
    
    # Pull down the list of gh usernames from our editorial team
    members = get_team_members()
    exclude = [
        "lwasser",
        "chayadecacao",
        "xuanxu",
    ]
    # Exclude members who are administrative but don't actually lead reviews
    editorial_team_gh = filter_members(members, exclude)

    # Open the csv file that contains domain info for editors and a list of gh usernames
    data_dir = Path("_data")
    editor_domains = pd.read_csv(data_dir / "editorial_team_domains.csv")
    editor_domains["gh_username"] = editor_domains["gh_username"].str.replace(
        "@", ""
    )

    if editorial_team_gh:
        editorial_team_df = pd.DataFrame(
            editorial_team_gh, columns=["gh_username"]
        )
# Merge the graphQL data with the github team data
# This will result in empty domain data but an accurate list of current editors.
all_editors = pd.merge(
    editorial_team_df, editor_domains, on="gh_username", how="outer"
)

output_file = data_dir / "editorial_team_domains.csv"
all_editors.to_csv(output_file, index=False)
