# Verification Script for Sensor (PowerShell)

# 1. Check Docker & MinIO
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker-compose up -d minio
} else {
    Write-Host "Skipping Docker start (assuming external or already running)..."
}

# 2. Setup Environment with uv
Write-Host "Setting up Python environment with uv..."

# Check for uv
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "uv is not installed. Please install it first (see WARP.md)."
    exit 1
}

# Create venv if missing
if (-not (Test-Path ".venv")) {
    Write-Host "Creating .venv..."
    uv venv
}

# Install dependencies
Write-Host "Installing dependencies..."
uv pip install -e .

# 3. Run Upload Script
Write-Host "Running upload script..."
# Use the python from .venv
$VENV_PYTHON = if ($IsWindows) { ".venv\Scripts\python.exe" } else { ".venv/bin/python" }
& $VENV_PYTHON verify_sensor_upload.py

# 4. Hint to run Dagster
Write-Host "`nTo run the Dagster UI:"
if ($IsWindows) {
    Write-Host ".venv\Scripts\dagster dev -m src.pipelines.definitions"
} else {
    Write-Host "source .venv/bin/activate; dagster dev -m src.pipelines.definitions"
}
