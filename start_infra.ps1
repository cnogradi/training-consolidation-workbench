# Start all infrastructure (MinIO, Neo4j, Weaviate)
Write-Host "Starting all infrastructure..."
docker-compose up -d

# Re-install dependencies (to pick up weaviate-client downgrade)
Write-Host "Ensuring dependencies are up to date..."
uv pip install -e .

Write-Host "Infrastructure started. You can now run the sensor verification."
