#!/usr/bin/env bash
# Start HiveMind backend (Unix/macOS)
# Usage: ./scripts/start-backend.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Starting HiveMind backend (shell script)"

if [ ! -d .venv ]; then
  echo "Creating virtual environment .venv..."
  python3 -m venv .venv
fi

PYTHON=.venv/bin/python
$PYTHON -m pip install --upgrade pip setuptools wheel
$PYTHON -m pip install -r backend/requirements.txt

echo "Running uvicorn backend.app.main:app on http://0.0.0.0:8000"
$PYTHON -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
