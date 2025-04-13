# PowerShell script to set up and run the String Frequency Analyzer project

# Stop on any error
$ErrorActionPreference = "Stop"

# Function to check if command exists
function Test-CommandExists {
    param ($command)
    $exists = $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
    return $exists
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Green

if (-not (Test-CommandExists "python")) {
    Write-Host "Python not found. Please install Python 3.8 or newer." -ForegroundColor Red
    exit 1
}

if (-not (Test-CommandExists "cargo")) {
    Write-Host "Cargo not found. Please install Rust." -ForegroundColor Red
    exit 1
}

# Create virtual environment if not exists
if (-not (Test-Path -Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Green
    python -m venv venv
}

# Activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Green
pip install -r requirements.txt

# Install the package in development mode
Write-Host "Installing Python package in development mode..." -ForegroundColor Green
pip install -e .

# Build the Rust application
Write-Host "Building Rust application..." -ForegroundColor Green
cargo build

# Start the Python API server in background
Write-Host "Starting API server in background..." -ForegroundColor Green
$pythonProcess = Start-Process -FilePath python -ArgumentList "api_server.py" -PassThru -NoNewWindow

# Wait for API server to start
Write-Host "Waiting for API server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Run the Rust application
Write-Host "Starting Rust GUI application..." -ForegroundColor Green
cargo run

# Cleanup when done
Write-Host "Cleaning up..." -ForegroundColor Green
if ($pythonProcess -ne $null) {
    Stop-Process -Id $pythonProcess.Id -Force
}

Write-Host "Done!" -ForegroundColor Green