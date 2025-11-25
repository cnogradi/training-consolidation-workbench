import os
import sys
from src.storage.neo4j import Neo4jClient

def verify_graph():
    try:
        client = Neo4jClient()
        # Check for any Course nodes
        courses = client.execute_query("MATCH (n:Course) RETURN n LIMIT 5")
        print(f"Found {len(courses)} Course nodes.")
        
        # Check for Concepts
        concepts = client.execute_query("MATCH (n:Concept) RETURN n LIMIT 5")
        print(f"Found {len(concepts)} Concept nodes.")
        
        if len(courses) > 0 and len(concepts) > 0:
            print("SUCCESS: Graph populated.")
            sys.exit(0)
        else:
            print("WARNING: Graph empty. Did you run the pipeline?")
            sys.exit(1)
    except Exception as e:
        print(f"Error connecting to Neo4j: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_graph()
