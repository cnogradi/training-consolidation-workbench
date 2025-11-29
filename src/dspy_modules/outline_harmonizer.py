"""
DSPy module for harmonizing multiple course outlines into a single consolidated curriculum.
"""
import dspy
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class SourceOutline(BaseModel):
    """A section from a source course"""
    bu: str = Field(description="Business unit this section is from")
    section_title: str = Field(description="Title of the section")
    concepts: List[str] = Field(description="Key concepts taught in this section")


class TargetSection(BaseModel):
    """A proposed section in the consolidated curriculum"""
    title: str = Field(description="Title for the target section")
    rationale: str = Field(description="Why this section is needed, what it combines")
    key_concepts: List[str] = Field(description="Top 3-5 concepts to teach")


class GenerateConsolidatedSkeleton(dspy.Signature):
    """
    Given multiple source course outlines, generate a consolidated curriculum skeleton 
    that intelligently merges concepts and eliminates redundancy.
    
    Focus on:
    - Identifying common themes across sources
    - Eliminating duplicate or highly overlapping concepts
    - Creating a logical learning progression
    - Combining related topics from different sources
    """
    source_outlines: str = dspy.InputField(
        desc="JSON array of source sections with their business unit, title, and concepts"
    )
    consolidated_plan: str = dspy.OutputField(
        desc="JSON array of target sections with title, rationale, and key_concepts"
    )


class OutlineHarmonizer(dspy.Module):
    """Module that harmonizes multiple course outlines into a single curriculum"""
    
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(GenerateConsolidatedSkeleton)
    
    def forward(self, source_outlines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate consolidated skeleton from source outlines.
        
        Args:
            source_outlines: List of dicts with keys: bu, section_title, concepts
            
        Returns:
            List of dicts with keys: title, rationale, key_concepts
        """
        import json
        
        # Convert to JSON string for DSPy
        source_json = json.dumps(source_outlines, indent=2)
        
        # Call DSPy
        result = self.generate(source_outlines=source_json)
        
        # Parse the output JSON
        try:
            consolidated = json.loads(result.consolidated_plan)
            return consolidated
        except json.JSONDecodeError as e:
            print(f"Error parsing DSPy output: {e}")
            print(f"Raw output: {result.consolidated_plan}")
            # Fallback: return a simple aggregated version
            return self._fallback_merge(source_outlines)
    
    def _fallback_merge(self, source_outlines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple fallback merge if DSPy fails"""
        # Group by similar section titles
        sections = []
        for source in source_outlines:
            sections.append({
                "title": source['section_title'],
                "rationale": f"Based on content from {source['bu']}",
                "key_concepts": source['concepts'][:5]
            })
        return sections
