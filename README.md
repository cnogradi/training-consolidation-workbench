# Training Consolidation Workbench

This project supports consolidation of training material from multiple business units into a single, unified curriculum across four engineering domains: software, electrical, systems, and mechanical.

## High-level architecture

- **Ingestion (Dagster + Unstructured)**
  - Dagster pipelines orchestrate extraction from Word, PowerPoint, and PDF source materials.
  - Unstructured is used to extract text, layout structure, and media references.
  - Extracted text, outlines, and media metadata are written to MinIO (S3-compatible) buckets.

- **Semantic extraction (Python + LLMs via Ollama/BAML/DSPy)**
  - Domain-aware pipelines generate:
    - Document/section embeddings for Weaviate.
    - Pre-extracted outlines and section hierarchies.
    - Semantic concepts and learning objectives for each section.
  - Results are stored in Weaviate (vector search) and optionally Neo4j for rich relationship graphs (e.g., concept dependencies across business units and domains).

- **Storage layer (MinIO + Weaviate + Neo4j)**
  - MinIO: raw documents, extracted text JSON, slide/page images, and versioned consolidation artifacts.
  - Weaviate: embeddings for sections, semantic concepts, and candidate consolidated content.
  - Neo4j (optional): graph of concepts, dependencies, and mappings from original to consolidated training.

- **Workbench UI (Python backend + web frontend)**
  - Backend exposes APIs for:
    - Loading original outlines per domain and business unit.
    - Querying semantic concepts and example source passages.
    - Previewing original slide/page images during consolidation.
    - Saving the evolving consolidated outline and merged content.
  - Frontend presents a "consolidation workbench" where domain experts can:
    - View original outlines and concepts side-by-side.
    - Drag-and-drop or otherwise assemble a new unified outline.
    - Ask for AI-assisted suggestions to merge or rewrite content.

## Next steps

- Define concrete Dagster jobs for ingestion and semantic extraction.
- Design Weaviate and Neo4j schemas for documents, sections, and concepts.
- Implement a minimal API for the workbench, then iterate on the UI.
