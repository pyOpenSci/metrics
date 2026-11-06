"""Regression tests for scripts/get-prs.py (year filtering, see gh-74)."""

import importlib.util
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "get-prs.py"
spec = importlib.util.spec_from_file_location("get_prs", SCRIPT)
get_prs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(get_prs)

START_2024 = datetime(2024, 1, 1)
START_2025 = datetime(2025, 1, 1)
CONTRIB_TYPES = {"pyos_staff": ["staff-user"], "bots": ["some-bot[bot]"]}


def make_item(created_at, closed_at=None, is_pr=False, user="contrib-user"):
    """Build a minimal GitHub issues/pulls API item."""
    item = {
        "title": f"item opened {created_at}",
        "created_at": created_at,
        "closed_at": closed_at,
        "state": "closed" if closed_at else "open",
        "labels": [],
        "user": {"login": user},
    }
    if is_pr:
        item["pull_request"] = {"url": "https://api.github.com/..."}
    return item


class FakeGitHubAPI:
    """Stand-in for pyosmeta GitHubAPI serving canned items per endpoint."""

    def __init__(self, issues=(), pulls=(), fail_for=()):
        self._items = {"issues": list(issues), "pulls": list(pulls)}
        self._fail_for = set(fail_for)
        self.endpoint_type = ""
        self.repo = ""
        self.api_endpoint = ""

    def _get_response_rest(self, endpoint):
        if self.repo in self._fail_for:
            raise RuntimeError(f"API error for {self.repo}")
        return self._items[self.endpoint_type]

    def get_user_info(self, gh_handle):
        return {"location": "Earth"}


def get_issues(api, start=START_2024, end=START_2025):
    return get_prs.get_repo_data(api, "repo", "issues", CONTRIB_TYPES, {}, start, end)


def test_year_boundaries_are_inclusive_start_exclusive_end():
    api = FakeGitHubAPI(
        issues=[
            make_item("2023-12-31T23:59:59Z"),
            make_item("2024-01-01T00:00:00Z"),
            make_item("2024-12-31T23:59:59Z"),
            make_item("2025-01-01T00:00:00Z"),
        ]
    )
    df = get_issues(api)
    assert list(df["date_opened"]) == [
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 12, 31, 23, 59, 59),
    ]


def test_cross_year_closure_is_filed_under_year_opened():
    opened_2024_closed_2025 = make_item("2024-11-15T10:00:00Z", "2025-02-01T10:00:00Z")
    opened_2023_closed_2024 = make_item("2023-11-15T10:00:00Z", "2024-02-01T10:00:00Z")
    api = FakeGitHubAPI(issues=[opened_2024_closed_2025, opened_2023_closed_2024])

    df_2024 = get_issues(api)
    assert len(df_2024) == 1
    assert df_2024.loc[0, "date_closed"] == datetime(2025, 2, 1, 10, 0, 0)
    assert df_2024.loc[0, "current_status"] == "closed"

    df_2025 = get_issues(api, START_2025, datetime(2026, 1, 1))
    assert df_2025.empty


def test_still_open_item_has_no_close_date():
    df = get_issues(FakeGitHubAPI(issues=[make_item("2024-06-01T00:00:00Z")]))
    assert df.loc[0, "date_closed"] is None
    assert df.loc[0, "current_status"] == "open"


def test_prs_are_not_double_counted_from_issues_endpoint():
    pr = make_item("2024-06-01T00:00:00Z", is_pr=True)
    issue = make_item("2024-06-02T00:00:00Z")
    # The issues endpoint returns PRs too; the pulls endpoint returns only PRs
    api = FakeGitHubAPI(issues=[issue, pr], pulls=[pr])

    df = get_prs.process_repo(api, "repo", CONTRIB_TYPES, {}, START_2024, START_2025)
    assert sorted(df["type"]) == ["issues", "pulls"]


def test_bots_are_skipped_and_staff_flagged():
    api = FakeGitHubAPI(
        issues=[
            make_item("2024-06-01T00:00:00Z", user="some-bot[bot]"),
            make_item("2024-06-01T00:00:00Z", user="staff-user"),
            make_item("2024-06-01T00:00:00Z", user="contrib-user"),
        ]
    )
    df = get_issues(api)
    assert list(df["contrib_type"]) == ["staff", "contributor"]


def test_process_repo_propagates_api_errors():
    api = FakeGitHubAPI(fail_for=["repo"])
    with pytest.raises(RuntimeError):
        get_prs.process_repo(api, "repo", CONTRIB_TYPES, {}, START_2024, START_2025)


def run_main(monkeypatch, tmp_path, api, year=2024):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(get_prs, "GitHubAPI", lambda **kwargs: api)
    monkeypatch.setattr(sys, "argv", ["get-prs.py", "--year", str(year)])
    get_prs.main()
    return tmp_path / "data" / f"{year}_all_issues_prs.csv"


def test_main_exits_nonzero_when_any_repo_fails(monkeypatch, tmp_path):
    api = FakeGitHubAPI(
        issues=[make_item("2024-06-01T00:00:00Z")], fail_for=["handbook"]
    )
    with pytest.raises(SystemExit, match="handbook"):
        run_main(monkeypatch, tmp_path, api)
    assert not (tmp_path / "data").exists()


def test_main_exports_when_all_repos_succeed(monkeypatch, tmp_path):
    api = FakeGitHubAPI(issues=[make_item("2024-06-01T00:00:00Z")])
    csv_path = run_main(monkeypatch, tmp_path, api)
    df = pd.read_csv(csv_path)
    # The fake serves one issue for every repo in the script's repo list
    assert len(df) == df["repo"].nunique()
    assert set(df.columns) >= {"date_opened", "date_closed", "repo", "type"}
