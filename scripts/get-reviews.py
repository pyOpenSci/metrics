"""
A script that parses ALL pyOpenSci reviews including presubmissions,
closed submissions, etc. This allows us to compile activity stats over time.
"""

import os
import re

import pandas as pd
import requests
from pyosmeta import ProcessIssues
from pyosmeta.github_api import GitHubAPI

pd.options.mode.chained_assignment = None

GRAPHQL_URL = "https://api.github.com/graphql"
REPO_OWNER = "pyOpenSci"
REPO_NAME = "software-submission"
# Keep batches modest vs GraphQL complexity / payload size.
LAST_COMMENT_BATCH_SIZE = 50

# Authoritative definition of label names and which status the package is at
ISSUE_MAP = {
    "New Submission!": "pre-review",
    "0/pre-review-checks": "pre-review",
    "0/seeking-editor": "seeking editor",
    "1/editor-assigned": "under-review",
    "2/seeking-reviewers": "under-review",
    "3/reviewers-assigned": "under-review",
    "4/reviews-in-awaiting-changes": "under-review",
    "5/awaiting-reviewer-response": "under-review",
    "6/pyOS-approved": "pyos-accepted",
    "7/under-joss-review": "under-joss-review",
    "8/joss-review-complete": "under-joss-review",
    "9/joss-approved": "joss-accepted",
}

# These labels indicate a package is accepted by PyOS
PYOS_ACCEPTED_LABELS = {
    "6/pyOS-approved",
    "7/under-joss-review",
    "8/joss-review-complete",
    "9/joss-approved",
}

# These labels indicate a package is accepted by JOSS
JOSS_ACCEPTED_LABELS = {"9/joss-approved"}

# These labels indicate a package has been submitted to JOSS
JOSS_SUBMITTED_LABELS = {
    "7/under-joss-review",
    "8/joss-review-complete",
    "joss-submission-pending",
}

SUBMISSION_TYPES = {
    "submission": list(ISSUE_MAP),
    "presubmission": ["presubmission"],
}

RE_LABEL_FORMAT = re.compile(r"(\d+)/[\w-]+")


def get_reviews(org, repo, labels):
    """
    Get reviews from a GitHub repository using pyosMeta.

    Parameters
    ----------
    org : str
        The organization name.
    repo : str
        The repository name.
    labels : list
        A list of labels to filter the reviews.

    Returns
    -------
    reviews : list
        A list of reviews from the specified repository.

    """
    github_api = GitHubAPI(
        org=org,
        repo=repo,
        labels=labels,
    )
    process_review = ProcessIssues(github_api)
    issues = process_review.get_issues()
    reviews, _ = process_review.parse_issues(issues)
    return reviews


def process_submissions(submission_type, labels):
    """Process review issues and return a pandas DataFrame with review metadata.

    Parameters
    ----------
    submission_type : str
        The type of submission.
    labels : list
        A list of labels to filter the reviews.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the processed submissions with the following columns:
        - package_name (str): The name of the package.
        - submitting_author (str): GitHub username of the submitting author.
        - editor (str): The GitHub username of the editor.
        - eic (str): The GitHub username of the editor-in-chief.
        - date_opened (datetime): The date the review was opened.
        - date_closed (datetime): The date the review was closed.
        - date_accepted (datetime): The date the review was accepted.
        - labels (list): The labels assigned to the review.
        - issue_num (str): The issue number associated with the review.
        - description (str): The description of the package.
        - categories (list): The categories assigned to the package.
    """
    reviews = get_reviews("pyopensci", "software-submission", labels)
    submission_table = [
        {
            "package_name": name,
            "submitting_author": getattr(
                review.submitting_author, "github_username", None
            ),
            "editor": getattr(review.editor, "github_username", None),
            "eic": getattr(review.eic, "github_username", None),
            "date_opened": review.created_at,
            "date_closed": review.closed_at,
            "date_accepted": review.date_accepted,
            "labels": review.labels,
            "issue_num": review.issue_link.split("/")[-1],
            "description": review.package_description,
            "categories": review.categories,
        }
        for name, review in reviews.items()
    ]

    return pd.DataFrame(submission_table)


def set_review_status(labels, issue_map):
    """Determines the review status of an issue based on the given label values.

    Parameters
    ----------
    labels : list
        A list of labels associated with the issue.
    issue_map : dict
        A dictionary mapping labels to their corresponding review status.

    Returns
    -------
    str
        The review status determined based on the labels and issue map.

    Notes
    ------------------
    - If the label "presubmission" is present in the labels list, the review
      status is set to "presubmission".
    - If the label "currently-out-of-scope" is present in the labels list, the
      review status is set to "out of scope".
    - If any of the labels "⌛ pending-maintainer-response" or "on-hold" are
      present in the labels list, the review status is set to "on hold".

    """

    highest_label = None

    if "presubmission" in labels:
        return "presubmission"
    elif "currently-out-of-scope" in labels:
        return "out of scope"
    elif any(
        label in labels for label in ["⌛ pending-maintainer-response", "on-hold"]
    ):
        return "on hold"

    status_labels = [
        label for label in labels if label in ISSUE_MAP and RE_LABEL_FORMAT.match(label)
    ]
    if status_labels:
        highest_label = max(
            status_labels,
            key=lambda x: int(x.split("/", 1)[0]),
        )

    return issue_map.get(highest_label)


def set_pyos_status(labels, status):
    """Return the pyOpenSci review status, collapsing all accepted stages.

    Parameters
    ----------
    labels : list
        A list of labels associated with the issue.
    status : str
        The review status returned by ``set_review_status``.

    Returns
    -------
    str
        "accepted" if the issue has any stage label from 6 to 9, otherwise
        ``status`` unchanged.

    Notes
    -----
    Acceptance takes precedence over "on hold" and "out of scope", so an
    accepted package that later gets one of those labels still counts as
    accepted.
    """
    if any(label in PYOS_ACCEPTED_LABELS for label in labels):
        return "accepted"
    return status


def set_joss_status(labels):
    """Return the JOSS status of a pyOpenSci-accepted package.

    Parameters
    ----------
    labels : list
        A list of labels associated with the issue.

    Returns
    -------
    str or None
        None if the package is not accepted by pyOpenSci, otherwise
        "accepted", "submitted" or "none".
    """
    if not any(label in PYOS_ACCEPTED_LABELS for label in labels):
        return None
    if any(label in JOSS_ACCEPTED_LABELS for label in labels):
        return "accepted"
    if any(label in JOSS_SUBMITTED_LABELS for label in labels):
        return "submitted"
    return "none"


def _parse_last_comment_nodes(comments):
    """Return (date, user) from GraphQL comment nodes; None if empty."""
    if not comments:
        return None, None
    last_comment = comments[0]
    author = last_comment.get("author") or {}
    return last_comment.get("createdAt"), author.get("login")


def get_last_comments(issue_nums, batch_size=LAST_COMMENT_BATCH_SIZE):
    """Batch-fetch last comment date/user for many issues via GraphQL aliases.

    Parameters
    ----------
    issue_nums : sequence
        Issue numbers to query.
    batch_size : int
        Max issues per GraphQL request.

    Returns
    -------
    dict[str, tuple]
        Maps issue number (as str) to ``(last_comment_date, last_comment_user)``.
        Missing or failed issues map to ``(None, None)``.
    """
    gh_token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Authorization": f"Bearer {gh_token}",
        "Content-Type": "application/json",
    }

    results = {}
    nums = [str(n) for n in issue_nums]

    for start in range(0, len(nums), batch_size):
        batch = nums[start : start + batch_size]
        alias_blocks = []
        for num in batch:
            alias_blocks.append(
                f"""
                i{num}: issue(number: {int(num)}) {{
                  comments(last: 1) {{
                    nodes {{
                      createdAt
                      author {{
                        login
                      }}
                    }}
                  }}
                }}
                """
            )

        query = f"""
        query {{
          repository(owner: "{REPO_OWNER}", name: "{REPO_NAME}") {{
            {"".join(alias_blocks)}
          }}
        }}
        """

        response = requests.post(
            GRAPHQL_URL,
            json={"query": query},
            headers=headers,
        )

        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response content: {response.content}")
            for num in batch:
                results[num] = (None, None)
            continue

        payload = response.json()
        if payload.get("errors"):
            print(f"GraphQL errors (batch starting {batch[0]}): {payload['errors']}")

        repo_data = (payload.get("data") or {}).get("repository") or {}
        for num in batch:
            issue_data = repo_data.get(f"i{num}")
            if not issue_data:
                print(f"Missing issue data for issue {num}")
                results[num] = (None, None)
                continue
            comments = issue_data.get("comments", {}).get("nodes", [])
            results[num] = _parse_last_comment_nodes(comments)

    return results


def attach_last_comments(df):
    """Join batched last-comment fields onto a submissions DataFrame."""
    comments_by_issue = get_last_comments(df["issue_num"].tolist())
    df["last_comment_date"] = df["issue_num"].map(
        lambda n: comments_by_issue.get(str(n), (None, None))[0]
    )
    df["last_comment_user"] = df["issue_num"].map(
        lambda n: comments_by_issue.get(str(n), (None, None))[1]
    )
    return df


def main():
    for submission_type, labels in SUBMISSION_TYPES.items():
        df = process_submissions(submission_type, labels)
        df["status"] = df["labels"].apply(set_review_status, args=(ISSUE_MAP,))
        df["pyos_status"] = [
            set_pyos_status(labels, status)
            for labels, status in zip(df["labels"], df["status"])
        ]
        df["joss_status"] = df["labels"].apply(set_joss_status)
        df = attach_last_comments(df)

        # Save csv file
        os.makedirs("data", exist_ok=True)
        csv_path = os.path.join("data", f"review_{submission_type}s.csv")
        df.to_csv(csv_path)
        print(f"{submission_type} processing done. Total: {len(df)}")


if __name__ == "__main__":
    main()
