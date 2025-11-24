# Verification Script for Module 1

# 1. Check Docker
Write-Host "Checking Docker..."
docker --version
if ($LASTEXITCODE -ne 0) { 
    Write-Error "Docker is not found. Please install Docker Desktop."
    exit 1
}

# 2. Start MinIO
Write-Host "Starting MinIO..."
docker-compose up -d minio
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to start MinIO."
    exit 1
}

# 3. Install Python Dependencies
Write-Host "Installing Python dependencies..."
pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install dependencies."
    exit 1
}

# 4. Create Test Data
Write-Host "Creating test data in data/raw..."
if (-not (Test-Path "data/raw")) {
    New-Item -ItemType Directory -Path "data/raw" | Out-Null
}
Set-Content -Path "data/raw/test_doc.txt" -Value "Hello, this is a test document for the training consolidation workbench."

# 5. Run Dagster Materialization
Write-Host "Running Dagster asset 'raw_documents'..."
# Set default env vars for local dev if not set
$Env:MINIO_ENDPOINT = "localhost:9000"
$Env:MINIO_ACCESS_KEY = "minioadmin"
$Env:MINIO_SECRET_KEY = "minioadmin"

dagster asset materialize -m src.pipelines.definitions -a raw_documents

if ($LASTEXITCODE -eq 0) {
    Write-Host "Success! Assets materialized."
    Write-Host "You can view the MinIO console at http://localhost:9001 to verify the 'images', 'text', and 'manifests' buckets."
} else {
    Write-Error "Dagster run failed."
}
