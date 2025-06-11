#!/bin/bash
set -euo pipefail

# Setup development environment for openalex-python
# Installs Python tools and caches dependencies for offline use.
# Run this once with internet access.

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ ! -f pyproject.toml ]; then
  echo "Run this script from the repository root" >&2
  exit 1
fi

# Install system packages on Debian/Ubuntu
if command -v apt-get >/dev/null; then
  sudo apt-get update
  sudo apt-get install -y python3.12 python3.12-venv python3-pip git curl build-essential
fi

PYTHON="python3.12"
if ! command -v "$PYTHON" >/dev/null; then
  echo "Python 3.12 is required" >&2
  exit 1
fi

VENV=".venv"
if [ ! -d "$VENV" ]; then
  "$PYTHON" -m venv "$VENV"
fi
source "$VENV/bin/activate"

# Upgrade packaging tools
pip install --upgrade pip setuptools wheel

WHEELHOUSE="wheelhouse"
mkdir -p "$WHEELHOUSE"

# Download dependencies for offline installation
pip download -d "$WHEELHOUSE" -r requirements.txt
pip download -d "$WHEELHOUSE" -r requirements-dev.txt
pip download -d "$WHEELHOUSE" poetry==1.8.2

# Install from local wheelhouse
pip install --no-index --find-links "$WHEELHOUSE" -r requirements.txt -r requirements-dev.txt
pip install --no-index --find-links "$WHEELHOUSE" poetry==1.8.2

# Install this package in editable mode
pip install --no-index --find-links "$WHEELHOUSE" -e .

# Install pre-commit hooks if configuration exists
if [ -f .pre-commit-config.yaml ]; then
  pre-commit install
fi

# Verify environment
ruff check .
mypy openalex
pytest

echo "Development environment is ready. Activate with 'source $VENV/bin/activate'"

