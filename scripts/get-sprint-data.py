import os

import requests
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
from functools import cached_property
from pydantic import BaseModel, HttpUrl
from enum import Enum
from tqdm import tqdm

load_dotenv()

# GitHub GraphQL endpoint
graphql_endpoint = "https://api.github.com/graphql"
ACCESS_TOKEN = os.getenv("GITHUB_TOKEN")


def get_ql_query_response(access_token, query):
    """Retrieves a response from a GraphQL endpoint.

    Parameters
    ----------
    query : str
        The GraphQL query string.
    access_token : str
        The access token used for authorization.

    Returns
    -------
    dict
        The JSON response from the GraphQL endpoint.
    """
    graphql_endpoint = "https://api.github.com/graphql"
    # Headers with authorization
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Make GraphQL query to fetch project board ID
    # print("Request URL:", graphql_endpoint)
    # print("Request Headers:", headers)
    # print("Request Body:", {"query": query})

    # Make GraphQL query to fetch project board ID
    response = requests.post(
        graphql_endpoint, json={"query": query}, headers=headers
    )

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Query failed to run with a status code {response.status_code}. Response: {response.text}"
        )
    return response.json()


def get_project_id(project_number, access_token):
    """GraphQL query to fetch project board ID
    this is working!

    """
    query = """
    query {
      organization(login: "pyopensci") {
        projectV2(number: %d) {
          id
        }
      }
    }
    """ % (
        project_number,
    )

    data = get_ql_query_response(query=query, access_token=access_token)

    # Extract project board ID
    try:
        project_id = data["data"]["organization"]["projectV2"]["id"]
        return project_id
    except (KeyError, TypeError):
        print(f"Project board not found for {project_number}. Response: {data}")
        return None


def get_project_field(project_id, access_token):
    """Next: get field (status) within our board?

    https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects#finding-the-node-id-of-a-field
    """

    query = (
        """
    query {
        node(id: "%s") {
            ... on ProjectV2 {
                fields(first: 20) {
                    nodes {
                        ... on ProjectV2Field {
                            id
                            name
                        }
                        ... on ProjectV2IterationField {
                            id
                            name
                            configuration {
                                iterations {
                                    startDate
                                    id
                                }
                            }
                        }
                        ... on ProjectV2SingleSelectField {
                            id
                            name
                            options {
                                id
                                name
                            }
                        }
                    }
                }
            }
        }
    }
    """
        % project_id
    )

    return get_ql_query_response(access_token=access_token, query=query)


def get_project_items(project_id, access_token):
    """
    Retrieve information about a project using GraphQL query.

    Parameters
    ----------
    project_id : str
      The ID of the project.
    access_token : str

    Returns
    -------
    dict
      The response containing project information.
    """
    items = []
    has_next_page = True
    end_cursor = None

    while has_next_page:
        query = """
        query {
          node(id: "%s") {
            ... on ProjectV2 {
              items(first: 100%s) {
                nodes {
                  id
                  content {
                    __typename
                    ... on Issue {
                      title
                      number
                      url
                      createdAt
                      closedAt
                      repository {
                        nameWithOwner
                      }
                      labels(first: 10) {
                        nodes {
                          name
                        }
                      }
                      assignees(first: 10) {
                        nodes {
                          login
                        }
                      }
                    }
                    ... on PullRequest {
                      title
                      number
                      url
                      createdAt
                      closedAt
                      repository {
                        nameWithOwner
                      }
                      labels(first: 10) {
                        nodes {
                          name
                        }
                      }
                      assignees(first: 10) {
                        nodes {
                          login
                        }
                      }
                    }
                  }
                  fieldValues(first: 10) {
                    nodes {
                      ... on ProjectV2ItemFieldSingleSelectValue {
                        name
                        field {
                          ... on ProjectV2SingleSelectField {
                            name
                          }
                        }
                      }
                    }
                  }
                }
                pageInfo {
                  endCursor
                  hasNextPage
                }
              }
            }
          }
        }
        """ % (
            project_id,
            f', after: "{end_cursor}"' if end_cursor else "",
        )

        response = get_ql_query_response(
            access_token=access_token, query=query
        )
        data = response["data"]["node"]["items"]
        items.extend(data["nodes"])
        has_next_page = data["pageInfo"]["hasNextPage"]
        end_cursor = data["pageInfo"]["endCursor"]

    # Add a field to track whether it is an issue or a PR
    for item in items:
        item_type = item["content"]["__typename"]
        item["type"] = "Issue" if item_type == "Issue" else "PullRequest"

    return items


class TaskType(str, Enum):
    issue = "Issue"
    pull_request = "PullRequest"


class Task(BaseModel):
    event: str
    title: str
    number: int
    url: HttpUrl
    type: TaskType
    repository: str
    organization: str = "pyopensci"
    created: str | None = None
    closed: str | None = None

    @property
    def api_url(self):
        if self.type == TaskType.issue:
            return f"https://api.github.com/repos/{self.organization}/{self.repository}/issues/{self.number}"
        elif self.type == TaskType.pull_request:
            return f"https://api.github.com/repos/{self.organization}/{self.repository}/pulls/{self.number}"
        else:
            raise ValueError(f"Unknown task type: {self.type}")

    @cached_property
    def api(self):
        response = requests.get(
            self.api_url,
            headers={"Authorization": f"token {ACCESS_TOKEN}"},
        )
        response.raise_for_status()
        return response.json()

    @property
    def author(self) -> str:
        return self.api["user"]["login"]

    @property
    def state(self) -> str:
        return self.api["state"]

    @property
    def json(self):
        """JSON blob of the task for export."""
        return {
            "event": self.event,
            "author": self.author,
            "title": self.title,
            "type": self.type.value,
            "repository": self.repository,
            "organization": self.organization,
            "state": self.state,
            "number": self.number,
            "created": self.created,
            "closed": self.closed,
            "url": self.url,
            "api_url": self.api_url,
        }


def parse_item(item):
    event = "N/A"
    for node in item["fieldValues"]["nodes"]:
        if node and node["field"]["name"] == "Status":
            event = node["name"]
            break
    org, repo = item["content"]["repository"]["nameWithOwner"].split("/")
    return Task(
        event=event,
        title=item["content"]["title"],
        url=item["content"]["url"],
        number=item["content"]["number"],
        type=TaskType(item["content"]["__typename"]),
        repository=repo,
        organization=org,
        created=item["content"]["createdAt"],
        closed=item["content"]["closedAt"],
    )


if __name__ == "__main__":
    print("PROCESSING SPRINT DATA")
    # pyOS project board - https://github.com/orgs/pyOpenSci/projects/12
    project_pk = 12
    project_id = get_project_id(project_pk, ACCESS_TOKEN)
    if project_id is None:
        raise ValueError(f"Project board not found for {project_pk}. Likely a permissions issue.")

    project_items = get_project_items(project_id, ACCESS_TOKEN)

    df = pd.DataFrame([parse_item(item).json for item in tqdm(project_items)])
    dir_path = Path("_data")
    file_path = dir_path / "sprint_data.csv"

    dir_path.mkdir(parents=True, exist_ok=True)
    df.to_csv(file_path, index=False)
