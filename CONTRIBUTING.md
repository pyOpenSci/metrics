# CONTRIBUTING to our metrics repository

Welcome to the metrics repository. We welcome contributions of all kinds,
large, small and in between.

To get started contributing be sure to fork and clone this repository.

## About the data in this repository

The data in the `_data/` directory of this repo, contain contributor data
for the pyOpenSci organization. This data includes:

* Contributor pull request and issue data
* Contributor data collected and parsed using the all-contributors bot
* Peer review data collected from our software-submission repository
* Editorial team data collected from our github editorial team (some data such as domain data are added manually)

## About the scripts in this repository

The `scripts/` directory contains utility scripts for data collection, parsing, and analysis:

* **get-editors.py**: Updates the editorial team CSV file with current editors by merging manually curated domain data and GitHub team membership (via GraphQL API). Output: `_data/editorial_team_domains.csv`.
* **get-package-data.py**: Retrieves package data from GitHub repositories using the GitHub API. Returns a dictionary of package information.
* **get-prs.py**: Parses all active pyOpenSci repositories to collect contributor activity (issues and PRs) for the current year, excluding bots. Outputs a CSV for tracking contribution growth.
* **get-review-contributors.py**: Extracts and stores review contributor data (editors/reviewers) from peer review YAML files, including location if available. Outputs: `review_contribs.csv`.
* **get-reviews.py**: Parses all pyOpenSci reviews (presubmissions, closed submissions, etc.) to compile activity stats over time. Uses pyosMeta utilities for processing.
* **get-sprint-data.py**: Collects and processes sprint-related issues and pull requests data from out GitHub sprint project board using GraphQL and REST APIs, with support for environment variables and progress tracking.

## How the scripts are used

The scripts above are run via a CI cron job with the exception of the get-editors.py script which right now
doesn't run successfully in CI. Luckily our editorial team rotates slowly so this item is ok to have to manually run locally and update for the time being.
