
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage.neo4j import Neo4jClient

def list_slides(limit=10):
    client = Neo4jClient()
    query = """
    MATCH (s:Slide)
    RETURN s.id as id, s.layout_style as layout, s.asset_type as type
    LIMIT $limit
    """
    results = client.execute_query(query, {"limit": limit})
    client.close()
    
    print(f"\n--- Found {len(results)} Slides (showing top {limit}) ---")
    for row in results:
        print(f"{row['id']}")

def update_slide_by_index(index, new_layout):
    client = Neo4jClient()
    # Get ID at index
    query_id = """
    MATCH (s:Slide)
    RETURN s.id as id
    ORDER BY s.id
    SKIP $skip
    LIMIT 1
    """
    results = client.execute_query(query_id, {"skip": int(index)})
    
    if not results:
        print(f"No slide found at index {index}")
        client.close()
        return

    slide_id = results[0]["id"]
    print(f"Found Slide at index {index}: {slide_id}")
    
    # Update
    query_update = """
    MATCH (s:Slide {id: $id})
    SET s.layout_style = $layout
    RETURN s.id as id, s.layout_style as layout
    """
    results_update = client.execute_query(query_update, {"id": slide_id, "layout": new_layout})
    client.close()
    
    if results_update:
        print(f"[SUCCESS] Updated Slide {slide_id} to layout '{new_layout}'")
    else:
        print(f"[ERROR] Failed to update Slide {slide_id}")

if __name__ == "__main__":
    load_dotenv()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "update" and len(sys.argv) == 4:
            update_slide_layout(sys.argv[2], sys.argv[3])
            
        elif cmd == "update_index" and len(sys.argv) == 4:
            update_slide_by_index(sys.argv[2], sys.argv[3])
            
        else:
             list_slides()
    else:
        list_slides()
