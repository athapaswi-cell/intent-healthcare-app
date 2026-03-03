# Start Backend Server (Run from project root or backend directory)
Write-Host "Starting Backend Server" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check if we're in backend directory or project root
if (Test-Path "$scriptDir\venv\Scripts\Activate.ps1") {
    # We're in backend directory
    $projectRoot = Split-Path -Parent $scriptDir
    $venvPath = "$scriptDir\venv"
    $requirementsPath = "$scriptDir\requirements.txt"
} elseif (Test-Path "$scriptDir\backend\venv\Scripts\Activate.ps1") {
    # We're in project root
    $projectRoot = $scriptDir
    $venvPath = "$scriptDir\backend\venv"
    $requirementsPath = "$scriptDir\backend\requirements.txt"
} else {
    Write-Host "ERROR: Could not find virtual environment!" -ForegroundColor Red
    Write-Host "Please run this script from the project root or backend directory." -ForegroundColor Yellow
    exit 1
}

# Change to project root
Set-Location $projectRoot

Write-Host "Project root: $projectRoot" -ForegroundColor Gray
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"

Write-Host "Installing/updating dependencies..." -ForegroundColor Yellow
pip install -q -r $requirementsPath

Write-Host ""
Write-Host "Starting FastAPI backend server..." -ForegroundColor Green
Write-Host "The server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pharmacy endpoint:" -ForegroundColor Yellow
Write-Host "  POST /api/v1/pharmacy/recommend-medications" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Set PYTHONPATH to project root and start the server
$env:PYTHONPATH = $projectRoot
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000


