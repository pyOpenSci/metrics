# Metrics repo workflow

# General

Keep your answers short and to the point.

## About the site

Quarto website + Python data pipeline for pyOpenSci peer-review and contributor metrics.

**Do not** start `nox -s serve`, Quarto preview, or other long-running servers unless the user asks. Prefer telling them which command to run.

## Architecture

```
scripts/get-*.py  →  _data/*.csv  →  *.qmd (pandas / Altair / Plotly / itables)  →  _site/
                         ↑
              pyosMeta + GitHub API (token)
```

- Site config: `_quarto.yml` (navbar, theme, `styles/styles.css`)
- Local helpers/theme: `pyosmetrics_pkg/` (`import pyosmetrics`)
- Deps: `pyproject.toml` + `uv.lock` (`pyosmetrics` via editable path `pyosmetrics_pkg`)
- Auth: copy `.env-default` → `.env` with `GITHUB_TOKEN=` (public-repo read token)
- Run scripts: `uv sync` then `uv run python scripts/get-….py`

## Directory map

| Path | Role |
| ------ | ------ |
| `peer-review/*.qmd` | Review status, editorial, trends, accepted packages |
| `contributors/*.qmd` | Contributor + sprint dashboards |
| `pyos-packages/*.qmd` | Package activity |
| `scripts/` | Data collection CLIs |
| `_data/` | Checked-in CSVs consumed by `.qmd` pages |
| `pyosmetrics_pkg/src/pyosmetrics/` | Shared parse helpers + Altair Poppins theme |
| `noxfile.py` | Local build sessions |
| `scripts/netlify-build.sh` + `netlify.toml` | Netlify build (`BASE_URL=/metrics` in prod) |

## Local build (user runs these)

```bash
uv sync                 # once / when deps change
uv run nox -s html      # static render → _site/
uv run nox -s serve     # quarto preview (live); user starts/stops this
uv run python scripts/get-review-contributors.py
```

Nox sessions call `uv sync --group build` and `uv run quarto …`.

Production path: `https://www.pyopensci.org/metrics/` (`BASE_URL=/metrics`).

## Data scripts → outputs

Most scripts refresh via `.github/workflows/update-pr-data.yml` (cron + PR + dispatch). That workflow uploads `_data` and opens a PR on `main`.

| Script | Output / notes |
| -------- | ---------------- |
| `get-prs.py` | `_data/{year}_all_issues_prs.csv` |
| `get-reviews.py` | `_data/review_submissions.csv`, `review_presubmissions.csv` (pyosMeta) |
| `get-review-contributors.py` | `_data/review_contribs.csv` |
| `get-package-data.py` | `_data/package_data.csv` |
| `get-sprint-data.py` | `_data/sprint_data.csv` — needs **project** access (`PROJECTS_READ` in Actions) |
| `get-editors.py` | `_data/editorial_team_domains.csv` — needs teams read (`PYOS_GHA_TEAMS_READ`); may need manual local run if CI fails |

Do not commit secrets. Never put tokens in scripts or CSVs.

## Editing `.qmd` pages

- Front matter: `jupyter: python3`; often `execute: echo: false`
- Prefer existing stack: `pandas`, `altair`, `plotly`/`panel`, `itables`
- Reuse `pyosmetrics` theme helpers (`load_poppins_font`, `poppins_theme`, etc.) instead of one-off chart styling
- Live GitHub pulls in pages use `pyosmeta` + `GITHUB_TOKEN` from the environment
- After structural navbar changes, update `_quarto.yml`
- Ask before rewriting narrative copy; fix typos/grammar silently

## Agent habits

1. Read the target `.qmd` / script and related `_data` columns before changing logic.
2. Prefer extending `pyosmetrics` helpers over duplicating parse/plot code in pages.
3. When adding a new dashboard page: add the `.qmd`, wire it in `_quarto.yml`, and document any new data dependency.
4. When changing a collector script: note which CSV columns dashboards rely on; avoid breaking column names without updating consumers.
5. Ask the user to run `nox -s html` (or `serve`) to verify renders — do not start servers yourself.
6. Keep commits scoped; only commit when asked. Use conventional commits.

## Related docs in-repo

- `README.md` — token setup + Nox
- `CONTRIBUTING.md` — script inventory and data overview
- `.github/workflows/update-pr-data.yml` — data refresh + PR automation
- `.github/workflows/deploy.yml` — Quarto render / Pages deploy
- `netlify.toml` — Netlify / deploy-preview build
