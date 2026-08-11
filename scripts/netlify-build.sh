#!/usr/bin/env bash
# Build the Quarto metrics site on Netlify.
#
# Requires Python (see PYTHON_VERSION in netlify.toml) and a GITHUB_TOKEN
# environment variable in the Netlify site settings for GitHub API access
# during render. A fine-grained public-repo read token is sufficient.
set -euo pipefail

pip install --upgrade pip
pip install -r requirements.txt
pip install quarto-cli

quarto render
