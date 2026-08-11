#!/usr/bin/env bash
# Build the Quarto metrics site on Netlify.
set -euo pipefail

pip install --upgrade pip
pip install -r requirements.txt
pip install quarto-cli

quarto render
