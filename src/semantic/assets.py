import json
from typing import Any, Dict
from dagster import asset, AssetExecutionContext
from src.ingestion.assets import CourseArtifactConfig, course_files_partition
from src.storage.dagster_resources import MinioResource, Neo4jResource, WeaviateResource
from src.ingestion.assets import BUCKET_NAME
from src.semantic.extraction import LLMExtractor

from src.semantic.harmonization import Harmonizer

@asset
def harmonize_concepts(context: AssetExecutionContext, neo4j: Neo4jResource):
    """
    Analyzes all Concepts in the graph and creates CanonicalConcepts to group synonyms.
    """
    context.log.info("Starting Concept Harmonization...")
    
    neo4j_client = neo4j.get_client()
    harmonizer = Harmonizer(neo4j_client)
    
    try:
        clusters = harmonizer.harmonize()
        context.log.info(f"Identified {len(clusters)} clusters.")
        
        harmonizer.apply_clusters(clusters)
        context.log.info("Harmonization applied to Graph.")
        
    except Exception as e:
        context.log.error(f"Harmonization failed: {e}")
        raise
    finally:
        neo4j_client.close()

@asset(partitions_def=course_files_partition)
def build_knowledge_graph(
    context: AssetExecutionContext,
    process_course_artifact: Dict[str, Any],
    minio: MinioResource,
    neo4j: Neo4jResource,
    weaviate: WeaviateResource
):
    """
    Takes the manifest from ingestion, runs semantic extraction, and populates the graph.
    """
    manifest = process_course_artifact
    course_id = manifest["course_id"]
    text_location = manifest["text_location"]
    
    context.log.info(f"Building Knowledge Graph for course: {course_id}")
    
    # 1. Initialize Clients
    minio_client = minio.get_client()
    neo4j_client = neo4j.get_client()
    weaviate_client = weaviate.get_client()
    llm = LLMExtractor() # Assuming Env vars are set for Ollama
    
    # 2. Load Text Data
    import tempfile
    with tempfile.NamedTemporaryFile() as tmp:
        minio_client.download_file(BUCKET_NAME, text_location, tmp.name)
        with open(tmp.name, 'r', encoding='utf-8') as f:
            text_elements = json.load(f)
            
    # 3. Reconstruct Full Text for Outline
    # Simple concatenation of text elements
    full_text = "\n".join([el.get("text", "") for el in text_elements if el.get("text")])
    
    # 4. Extract Outline & Create Course/Section Nodes
    context.log.info("Extracting Outline...")
    try:
        outline = llm.extract_outline(full_text)
        
        # Create Course Node with Metadata
        metadata = manifest.get("metadata", {})
        neo4j_client.execute_query(
            """
            MERGE (c:Course {id: $id}) 
            SET c.title = $title,
                c.business_unit = $business_unit,
                c.version = $version,
                c.delivery_method = $delivery,
                c.duration_hours = $duration,
                c.audience = $audience,
                c.level = $level,
                c.discipline = $discipline
            """,
            {
                "id": course_id, 
                "title": manifest["filename"], # Or metadata.get('course_title') if preferred
                "business_unit": metadata.get("business_unit"),
                "version": metadata.get("version"),
                "delivery": metadata.get("current_delivery_method"),
                "duration": metadata.get("duration_hours"),
                "audience": metadata.get("audience"),
                "level": metadata.get("level_of_material"),
                "discipline": metadata.get("engineering_discipline")
            }
        )
        
        # Create Sections recursively
        def create_section_nodes(sections, parent_id):
            for i, sec in enumerate(sections):
                sec_id = f"{parent_id}_s{i}"
                neo4j_client.execute_query(
                    """
                    MERGE (s:Section {id: $id}) 
                    SET s.title = $title, s.level = $level
                    WITH s
                    MATCH (p {id: $parent_id})
                    MERGE (p)-[:HAS_SECTION]->(s)
                    """,
                    {"id": sec_id, "title": sec.title, "level": sec.level, "parent_id": parent_id}
                )
                create_section_nodes(sec.subsections, sec_id)
                
        create_section_nodes(outline.sections, course_id)
        context.log.info("Outline Graph Created.")
        
    except Exception as e:
        context.log.error(f"Outline extraction failed: {e}")

    # 5. Process Slides/Pages (Concept Extraction & Vector Indexing)
    # Group elements by page number (if available) or just chunk?
    # Unstructured usually provides "page_number" in metadata.
    
    from collections import defaultdict
    pages = defaultdict(list)
    
    # Logic to handle missing page numbers by chunking
    current_chunk_page = 1
    current_chunk_size = 0
    CHUNK_LIMIT = 1500 # Approx 250-300 words per "slide" if no page breaks
    
    for el in text_elements:
        metadata = el.get("metadata", {})
        text = el.get("text", "")
        
        if "page_number" in metadata:
            # Use explicit page number from extractor
            page_num = metadata["page_number"]
            pages[page_num].append(text)
        else:
            # Fallback: Assign to synthetic page chunks
            pages[current_chunk_page].append(text)
            current_chunk_size += len(text)
            if current_chunk_size > CHUNK_LIMIT:
                current_chunk_page += 1
                current_chunk_size = 0
        
    # Ensure Weaviate Class exists with text vectorizer enabled
    weaviate_client.ensure_class({
        "class": "SlideText",
        "vectorizer": "text2vec-transformers",  # Enable semantic search
        "moduleConfig": {
            "text2vec-transformers": {
                "vectorizeClassName": False  # Don't vectorize the class name, just the properties
            }
        },
        "properties": [
            {"name": "text", "dataType": ["text"], "moduleConfig": {"text2vec-transformers": {"skip": False, "vectorizePropertyName": False}}},
            {"name": "course_id", "dataType": ["string"], "moduleConfig": {"text2vec-transformers": {"skip": True}}},
            {"name": "slide_id", "dataType": ["string"], "moduleConfig": {"text2vec-transformers": {"skip": True}}},
        ]
    })

    for page_num, texts in pages.items():
        slide_text = "\n".join(texts)
        if not slide_text.strip():
            continue
            
        slide_id = f"{course_id}_p{page_num}"
        context.log.info(f"Processing Slide {page_num} (ID: {slide_id})")
        
        # Derive asset type from filename
        import os
        filename = manifest["filename"]
        file_ext = os.path.splitext(filename)[1].upper().replace('.', '')  # e.g., "PPTX"
        asset_type = file_ext if file_ext in ["PDF", "PPTX", "DOCX", "PPT", "DOC"] else "Unknown"
        
        # Create Slide Node
        neo4j_client.execute_query(
            """
            MATCH (c:Course {id: $course_id})
            MERGE (sl:Slide {id: $id})
            SET sl.number = $page_num, 
                sl.text = $text,
                sl.asset_type = $asset_type
            MERGE (c)-[:HAS_SLIDE]->(sl)
            """,
            {"course_id": course_id, "id": slide_id, "page_num": page_num, "text": slide_text[:500], "asset_type": asset_type}
        )
        
        # Extract Concepts
        try:
            content = llm.extract_concepts(slide_text)
            
            # Create Concept Nodes & Links with salience scores
            for concept in content.concepts:
                # Get salience score, default to 0.5 if not provided
                salience = getattr(concept, 'salience', 0.5)
                
                neo4j_client.execute_query(
                    """
                    MERGE (con:Concept {name: $name})
                    SET con.description = $desc
                    WITH con
                    MATCH (sl:Slide {id: $slide_id})
                    MERGE (sl)-[t:TEACHES]->(con)
                    SET t.salience = $salience
                    """,
                    {
                        "name": concept.name, 
                        "desc": concept.description, 
                        "slide_id": slide_id,
                        "salience": salience
                    }
                )
        except Exception as e:
            context.log.error(f"Concept extraction failed for slide {slide_id}: {e}")

        # Vector Indexing
        try:
            weaviate_client.add_object(
                data_object={
                    "text": slide_text,
                    "course_id": course_id,
                    "slide_id": slide_id
                },
                class_name="SlideText"
            )
        except Exception as e:
            context.log.error(f"Vector indexing failed for slide {slide_id}: {e}")

    # 6. Aggregate Concepts to Section Summaries
    context.log.info("Aggregating concepts to Section summaries...")
    try:
        # Aggregate concepts from Slides to Sections using salience-weighted ranking
        # Scoped to this course only
        aggregation_query = """
        MATCH (c:Course {id: $course_id})-[:HAS_SECTION]->(sec:Section)
        OPTIONAL MATCH (sec)-[:HAS_SECTION*0..]->(child:Section)
        OPTIONAL MATCH (child)-[:HAS_SLIDE]->(s:Slide)
        OPTIONAL MATCH (s)-[t:TEACHES]->(con:Concept)
        WITH sec, con.name as concept_name, sum(coalesce(t.salience, 0.5)) as total_salience
        WHERE concept_name IS NOT NULL
        WITH sec, concept_name, total_salience
        ORDER BY sec.id, total_salience DESC
        WITH sec, collect({name: concept_name, salience: total_salience}) as concepts
        SET sec.concept_summary = [x IN concepts[0..5] | x.name]
        RETURN sec.id as section_id, sec.title as section_title, sec.concept_summary as summary
        """
        
        results = neo4j_client.execute_query(aggregation_query, {"course_id": course_id})
        
        for row in results:
            context.log.info(f"Section '{row['section_title']}': {row['summary']}")
        
        context.log.info(f"Aggregated concepts for {len(results)} sections")
        
    except Exception as e:
        context.log.error(f"Concept aggregation failed: {e}")
        # Don't fail the entire job if aggregation fails

    neo4j_client.close()
    return {"course_id": course_id, "status": "processed"}
