#!/usr/bin/env bash
set -euo pipefail

if command -v mamba >/dev/null 2>&1; then
  mamba env create -f environment.yml
elif command -v conda >/dev/null 2>&1; then
  conda env create -f environment.yml
else
  python -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -r requirements.txt
fi

echo "Environment ready. Activate with: conda activate hackaton or source .venv/bin/activate"
