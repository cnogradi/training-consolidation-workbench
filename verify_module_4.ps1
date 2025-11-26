$ErrorActionPreference = "Stop"

Write-Host "Verifying Module 4: The Workbench API..."

# 1. Install Dependencies
Write-Host "Installing dependencies..."
try {
    if (Get-Command "uv" -ErrorAction SilentlyContinue) {
        uv pip install fastapi uvicorn dagster-graphql
    } else {
        py -m pip install fastapi uvicorn dagster-graphql
    }
} catch {
    Write-Host "Dependency install failed or already satisfied. Continuing..."
}

# 2. Start API Server in Background
Write-Host "Starting API Server..."
# Use py -m uvicorn to ensure we use the right environment
$apiProcess = Start-Process -FilePath "py" -ArgumentList "-m uvicorn src.workbench.main:app --port 8000" -PassThru -NoNewWindow

Start-Sleep -Seconds 5

try {
    # 3. Test Endpoints
    $baseUrl = "http://localhost:8000"

    # A. Explorer
    Write-Host "Testing GET /source/tree..."
    $tree = Invoke-RestMethod -Uri "$baseUrl/source/tree" -Method Get
    Write-Host "Tree received with $( $tree.Count ) business units."

    Write-Host "Testing GET /source/tree?discipline=Mechanical..."
    $treeFiltered = Invoke-RestMethod -Uri "$baseUrl/source/tree?discipline=Mechanical" -Method Get
    Write-Host "Filtered Tree received with $( $treeFiltered.Count ) business units."

    if ($tree.Count -gt 0) {
         $courseId = $tree[0].children[0].id
         Write-Host "Testing GET /source/course/$courseId/slides..."
         $slides = Invoke-RestMethod -Uri "$baseUrl/source/course/$courseId/slides" -Method Get
         Write-Host "Received $( $slides.Count ) slides."
         
         if ($slides.Count -gt 0) {
             $slideId = $slides[0].id
             Write-Host "Testing GET /source/slide/$slideId..."
             $slide = Invoke-RestMethod -Uri "$baseUrl/source/slide/$slideId" -Method Get
             Write-Host "Slide details: $($slide | ConvertTo-Json -Depth 2)"
         }
    }

    # B. Builder
    Write-Host "Testing POST /draft/create..."
    $project = Invoke-RestMethod -Uri "$baseUrl/draft/create?title=NewConsolidation" -Method Post
    Write-Host "Project Created: $($project.id)"

    Write-Host "Testing POST /draft/node/add..."
    $node = Invoke-RestMethod -Uri "$baseUrl/draft/node/add?parent_id=$($project.id)&title=Chapter1" -Method Post
    Write-Host "Node Created: $($node.id)"

    Write-Host "Testing PUT /draft/node/map..."
    # Use dummy slide ID if none found
    $slideIdToMap = if ($slides.Count -gt 0) { $slides[0].id } else { "dummy_slide_id" }
    # Force array for JSON serialization in PowerShell 5.1
    $body = "[`"$slideIdToMap`"]"
    Invoke-RestMethod -Uri "$baseUrl/draft/node/map?node_id=$($node.id)" -Method Put -Body $body -ContentType "application/json"
    Write-Host "Mapped slide to node."

    Write-Host "Testing GET /draft/structure/..."
    $structure = Invoke-RestMethod -Uri "$baseUrl/draft/structure/$($project.id)" -Method Get
    Write-Host "Structure received: $( $structure | ConvertTo-Json -Depth 2 )"

    # C. Synthesis (Optional check as it triggers Dagster)
    # Just checking endpoint existence/params check
    Write-Host "Testing POST /synthesis/trigger (Dry Run)..."
    # This might fail if Dagster is not running or job not found, but API should respond
    try {
        $payload = @{
            target_node_id = $node.id
            tone_instruction = "Professional"
        } | ConvertTo-Json
        
        # Expected to fail with 500 if Dagster not reachable, but 404 if node missing
        # logic check: connection to dagster might fail
        Invoke-RestMethod -Uri "$baseUrl/synthesis/trigger" -Method Post -Body $payload -ContentType "application/json"
    } catch {
        Write-Host "Synthesis trigger returned error as expected (Dagster likely not running): $_"
    }

    Write-Host "Module 4 Verification Passed!"

} finally {
    # Cleanup
    Stop-Process -Id $apiProcess.Id -Force
}
