@echo off
REM Start HiveMind backend (Windows CMD)
REM Usage: from repo root run: scripts\start-backend.bat

REM Create venv if missing
if not exist .venv\Scripts\python.exe (
    echo Creating virtual environment .venv...
    python -m venv .venv
)

REM Upgrade packaging tools
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel

REM Install requirements
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt

REM Run server
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
pause