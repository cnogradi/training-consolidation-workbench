# Training Consolidation Workbench

This project supports consolidation of training material from multiple business units into a single, unified curriculum across four engineering domains: software, electrical, systems, and mechanical.

## High-level Architecture

- **Module 1: Ingestion (Dagster + Unstructured + MinIO)**
  - **Input**: Word, PowerPoint, and PDF files uploaded to MinIO (`source_docs` -> `training-content` bucket).
  - **Orchestration**: Dagster sensor (`course_upload_sensor`) detects new files.
  - **Extraction**:
    - `unstructured` extracts text and metadata.
    - `pdf2image` / `libreoffice` renders high-res images of slides/pages.
    - **Output**: JSON artifacts and PNG images stored in MinIO under `{course_id}/generated/`.

- **Module 2: The Cartographer (Neo4j + Weaviate + BAML)**
  - **Semantic Extraction**: A Dagster asset (`build_knowledge_graph`) processes ingested text.
  - **Graph Construction**:
    - Nodes: `Course`, `Section`, `Slide`, `Concept`.
    - Edges: `HAS_SECTION`, `HAS_SLIDE`, `TEACHES`.
  - **Vector Indexing**: Slide text is embedded and stored in **Weaviate** for semantic search.

- **Module 3: The Harmonizer (DSPy + Neo4j)**
  - **Concept Alignment**: DSPy (LLM) analyzes extracted concepts to find synonyms and duplicates.
  - **Harmonization**: Creates `CanonicalConcept` nodes in Neo4j to group disparate terms (e.g., "E-Stop" vs "Emergency Stop").

- **Module 4: The Workbench (FastAPI + React + Tailwind)**
  - **Backend (FastAPI)**:
    - Serves course hierarchies (`/source/tree`) and slide details (`/source/slide/{id}`).
    - Manages the "Consolidated Draft" state in Neo4j.
    - Triggers AI synthesis via Dagster GraphQL (`/synthesis/trigger`).
  - **Frontend (React)**:
    - **Source Browser**: Visualizes legacy content filtered by Engineering Discipline.
    - **Consolidation Canvas**: A Drag-and-Drop workspace to build the new curriculum.
    - **AI Synthesis**: Generates consolidated text from selected source slides.

## Prerequisites

- **Docker**: To run MinIO, Neo4j, Weaviate, and Dagster.
- **Python 3.10+**: With `uv` recommended for dependency management.
- **Node.js 18+**: For the frontend.

## Setup & Installation

1.  **Start Infrastructure**
    ```powershell
    ./start_infra.ps1
    ```
    This spins up Docker containers for MinIO, Neo4j, Weaviate, and the Dagster Daemon.

2.  **Initialize Environment**
    Create a `.env` file in the root (see `.env.example`) with credentials for OpenAI/Ollama, Neo4j, etc.

3.  **Install Python Dependencies**
    ```powershell
    uv pip install -e .
    ```

4.  **Install Frontend Dependencies**
    ```powershell
    cd frontend
    npm install
    cd ..
    ```

## Running the Workbench

### 1. Start the Backend API
This serves the REST API for the frontend.
```powershell
uvicorn src.workbench.main:app --reload --port 8000
```

### 2. Start the Frontend
This launches the React UI (Vite).
```powershell
./run_frontend.ps1
# Or manually: cd frontend; npm run dev
```
Access the UI at **http://localhost:5173**.

### 3. Start Dagster (Optional for Dev)
If you need to inspect pipelines or trigger jobs manually.
```powershell
dagster dev
```

## Data Management

### Ingesting Data (Priming the Sensor)
To upload source documents (`.pdf`, `.pptx`, `.docx`) from the `source_docs/` folder into the system:
```powershell
./prime_sensor.ps1
```
This triggers the ingestion pipeline automatically.

### Resetting Data
To **wipe all data** from Neo4j and Weaviate (useful for testing):
```powershell
./purge_data.ps1
```

### Debugging & Sync
If the UI shows blank images or missing courses, the Neo4j graph might be out of sync with MinIO storage. Run:
```powershell
py sync_graph.py
```
This scans MinIO and rebuilds the graph nodes to match actual files.

## Development Notes

- **Frontend Configuration**: If your backend runs on a different port, update `frontend/.env`:
  ```env
  VITE_API_URL=http://localhost:YOUR_PORT
  ```
- **LLM Configuration**: Ensure `OLLAMA_BASE_URL` or OpenAI keys are set in `.env` for Modules 2 & 3.
