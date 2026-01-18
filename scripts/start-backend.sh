#!/usr/bin/env bash
# Start HiveMind backend (Unix/macOS)
# Usage: ./scripts/start-backend.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Starting HiveMind backend (shell script)"

# Detect python executable (prefer python3)
if command -v python3 >/dev/null 2>&1; then
  PY_CMD=python3
elif command -v python >/dev/null 2>&1; then
  PY_CMD=python
else
  echo "Error: no python interpreter found (python3 or python)." >&2
  exit 1
fi

if [ ! -d .venv ]; then
  echo "Creating virtual environment .venv using $PY_CMD..."
  $PY_CMD -m venv .venv
fi

PYTHON=.venv/bin/python
$PYTHON -m pip install --upgrade pip setuptools wheel
$PYTHON -m pip install -r backend/requirements.txt

# Use Railway provided PORT if available, default to 8000
PORT=${PORT:-8000}

echo "Running uvicorn backend.app.main:app on http://0.0.0.0:$PORT"
$PYTHON -m uvicorn backend.app.main:app --host 0.0.0.0 --port "$PORT"
