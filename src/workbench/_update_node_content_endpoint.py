
@app.put("/draft/node/content")
def update_node_content(node_id: str, content_markdown: str = Body(..., embed=True)):
    """
    Updates the content_markdown property of a TargetNode.
    Used for auto-saving edited synthesis content from the TipTap editor.
    """
    query = """
    MATCH (t:TargetNode {id: $node_id})
    SET t.content_markdown = $content
    RETURN t.id as id
    """
    result = neo4j_client.execute_query(query, {"node_id": node_id, "content": content_markdown})
    
    if not result:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return {"status": "success", "node_id": node_id}
