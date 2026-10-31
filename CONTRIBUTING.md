# CONTRIBUTING to our metrics repository

Welcome to the metrics repository. We welcome contributions of all kinds,
large, small and in between.

To get started contributing be sure to fork and clone this repository.

## About the data in this repository

The data in the `data/` directory of this repo, contain contributor data
for the pyOpenSci organization. This data includes:

* Contributor pull request and issue data
* Contributor data collected and parsed using the all-contributors bot
* Peer review data collected from our software-submission repository
* Editorial team membership from website board YAML plus `manual-editorial-roster.yml` (pyosMeta); profile data maintained in `data/editor_profiles.csv`

## About the scripts in this repository

The `scripts/` directory contains utility scripts for data collection, parsing, and analysis:

* **get-editors.py**: Merges website `editorial-board.yml` / `emeritus-editors.yml` with `manual-editorial-roster.yml` (same rules as pyosMeta `merge_manual_roster`), then joins profiles from `data/editor_profiles.csv`. Outputs: `data/editorial_team_domains.csv`, `data/emeritus_editor_domains.csv`. Add or update editor metadata in `data/editor_profiles.csv`; the output CSVs are generated files. How the roster YAML is produced, and when, is in the handbook's [data workflows](https://www.pyopensci.org/handbook/community/infrastructure/data-process.html) page.
* **get-package-data.py**: Loads website `packages.yml` via pyosMeta (`PACKAGES_RAW_URL`) and writes `data/package_data.csv`.
* **get-prs.py**: Parses all active pyOpenSci repositories to collect contributor activity (issues and PRs), excluding bots. Outputs `data/{year}_all_issues_prs.csv` for tracking contribution growth. Each file contains only items **opened** in that year (`2018_2023_all_issues_prs.csv` covers 2018 through 2023); an item opened in 2024 and closed in 2025 stays in the 2024 file, with `date_closed` set. The biweekly cron run refreshes the current year. To refresh close dates and status for an earlier year, run `uv run python scripts/get-prs.py --year 2024` (or `--historical` for the 2018-2023 file).
* **get-review-contributors.py**: Loads website `contributors.yml` via pyosMeta (`CONTRIBUTORS_RAW_URL`), validates with `PersonModel`, and writes `data/review_contribs.csv`.
* **get-reviews.py**: Parses all pyOpenSci reviews (presubmissions, closed submissions, etc.) to compile activity stats over time. Uses pyosMeta utilities for processing.
* **get-sprint-data.py**: Collects sprint issue/PR data from the GitHub sprint project board via GraphQL (including author and state). Output: `data/sprint_data.csv`.

## How the scripts are used

The scripts above are run via a CI cron job.

## Running scripts locally

Install [uv](https://docs.astral.sh/uv/), copy `.env-default` to `.env` with a
GitHub token (see the README), then:

```bash
uv sync
uv run python scripts/get-review-contributors.py
```

CI uses the same pattern (`uv sync --frozen --no-dev` then
`uv run python scripts/…`). Dependencies live in `pyproject.toml` /
`uv.lock` — not `requirements.txt`.
