# Start the HiveMind backend (Windows PowerShell)
# Usage: Open PowerShell in repo root and run: .\scripts\start-backend.ps1
# This script will:
#  - create a .venv if missing
#  - install/upgrade pip, setuptools, wheel
#  - install backend/requirements.txt
#  - launch the uvicorn server

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir/..  # ensure repo root

Write-Host "Starting HiveMind backend (PowerShell script)" -ForegroundColor Green

# Ensure python is available
try {
    python -c "import sys; print(sys.executable)" | Out-Null
} catch {
    Write-Error "Python not found in PATH. Install Python 3.10+ and try again."
    exit 1
}

# Create venv if missing
if (!(Test-Path -Path .venv)) {
    Write-Host "Creating virtual environment .venv..."
    python -m venv .venv
}

$python = Join-Path -Path (Resolve-Path .venv) -ChildPath 'Scripts\python.exe'
if (!(Test-Path $python)) {
    Write-Error "venv python not found at $python"
    exit 1
}

# Upgrade packaging tools
Write-Host "Upgrading pip, wheel, setuptools..."
& $python -m pip install --upgrade pip setuptools wheel

# Install backend requirements
Write-Host "Installing backend/requirements.txt..."
& $python -m pip install -r backend/requirements.txt

# Run the server
Write-Host "Running uvicorn backend.app.main:app on http://0.0.0.0:8000 (CTRL+C to stop)" -ForegroundColor Cyan
& $python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
