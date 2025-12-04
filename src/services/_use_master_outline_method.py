    def _use_master_outline(self, master_course_id: str) -> List[Dict]:
        """
        Use a master course's outline as the structure for the new curriculum.
        Returns a list of sections with titles, rationale, and key_concepts.
        """
        query = """
        MATCH (c:Course {id: $course_id})-[:HAS_SECTION*]->(s:Section)
        OPTIONAL MATCH (s)-[:COVERS]->(con:Concept)
        WITH s, collect(distinct con.name) as concepts
        RETURN s.id as id,
               s.title as title,
               s.level as level,
               coalesce(s.concept_summary, concepts, []) as concepts
        ORDER BY s.id
        """
        results = self.neo4j_client.execute_query(query, {"course_id": master_course_id})
        
        sections = []
        for row in results:
            sections.append({
                'title': row['title'],
                'rationale': f"Section from master outline: {row['title']}",
                'key_concepts': row.get('concepts', [])[:10]  # Limit to 10 concepts
            })
        
        return sections
