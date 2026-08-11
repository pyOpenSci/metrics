#!/usr/bin/env bash
# Build the Quarto metrics site on Netlify.
set -euo pipefail

curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="${HOME}/.local/bin:${PATH}"

uv sync --frozen --no-dev --group build
uv run quarto render
