import os
import dspy
from typing import List, Dict
from pydantic import BaseModel, Field
from src.storage.neo4j import Neo4jClient

class ConceptCluster(BaseModel):
    canonical_name: str = Field(description="The standardized, canonical name for this group of concepts.")
    description: str = Field(description="A consolidated definition of what this concept represents.")
    source_concepts: List[str] = Field(description="List of original concept names that belong to this cluster.")

class HarmonizationSignature(dspy.Signature):
    """
    Analyze a list of technical concepts and group them into semantic clusters.
    Identify synonyms, acronyms, and variations (e.g., 'E-Stop' and 'Emergency Halt').
    Produce a list of canonical concepts.
    """
    concepts: List[str] = dspy.InputField(desc="List of concept names to analyze.")
    clusters: List[ConceptCluster] = dspy.OutputField(desc="List of consolidated concept clusters.")

class Harmonizer:
    def __init__(self, neo4j_client: Neo4jClient):
        self.neo4j = neo4j_client
        
        # Configure DSPy with Ollama
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model_name = os.getenv("OLLAMA_MODEL", "gpt-oss:120b")
        
        # dspy.Ollama is the standard provider
        self.lm = dspy.OllamaLocal(model=model_name, base_url=base_url, timeout_ms=120000)
        dspy.settings.configure(lm=self.lm)
        
        self.module = dspy.TypedPredictor(HarmonizationSignature)

    def fetch_concepts(self) -> List[str]:
        """Fetch all unique concept names from Neo4j."""
        query = "MATCH (c:Concept) RETURN DISTINCT c.name as name"
        results = self.neo4j.execute_query(query)
        return [r["name"] for r in results if r.get("name")]

    def harmonize(self) -> List[ConceptCluster]:
        """Fetch, cluster, and return clusters."""
        concepts = self.fetch_concepts()
        if not concepts:
            return []
            
        # If list is too large, we might need to chunk it. 
        # For now, assuming reasonable size for prompt context.
        print(f"Harmonizing {len(concepts)} concepts...")
        
        prediction = self.module(concepts=concepts)
        return prediction.clusters

    def apply_clusters(self, clusters: List[ConceptCluster]):
        """Write CanonicalConcept nodes and relationships to Neo4j."""
        for cluster in clusters:
            # Create Canonical Node
            self.neo4j.execute_query(
                """
                MERGE (cc:CanonicalConcept {name: $name})
                SET cc.description = $desc
                """,
                {"name": cluster.canonical_name, "desc": cluster.description}
            )
            
            # Link sources
            for source_name in cluster.source_concepts:
                self.neo4j.execute_query(
                    """
                    MATCH (c:Concept {name: $source_name})
                    MATCH (cc:CanonicalConcept {name: $canon_name})
                    MERGE (c)-[:ALIGNS_TO]->(cc)
                    """,
                    {"source_name": source_name, "canon_name": cluster.canonical_name}
                )
                print(f"Linked '{source_name}' -> '{cluster.canonical_name}'")
