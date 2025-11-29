"""
DSPy module for synthesizing slide content into a consolidated markdown section.
"""
import dspy
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class GenerateSectionContent(dspy.Signature):
    """
    Synthesize a cohesive training manual section from multiple source slides.
    
    Follow these rules:
    1. Integrate content from all provided slides.
    2. Follow the specific instructions provided (e.g., tone, emphasis).
    3. Use professional markdown formatting (headers, bullet points, bold text).
    4. Ensure smooth transitions between topics.
    5. Do not explicitly mention "Slide 1" or "Slide 2" unless necessary for context.
    """
    slide_content: str = dspy.InputField(
        desc="Text content from source slides, labeled by Slide ID"
    )
    instruction: str = dspy.InputField(
        desc="Specific instructions for synthesis (tone, audience, focus)"
    )
    markdown_content: str = dspy.OutputField(
        desc="The generated markdown content for the section"
    )


class ContentSynthesizer(dspy.Module):
    """Module that synthesizes slide content into markdown"""
    
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(GenerateSectionContent)
    
    def forward(self, slides: List[Dict[str, Any]], instruction: str) -> str:
        """
        Generate markdown content from slides.
        
        Args:
            slides: List of dicts with keys: id, text
            instruction: Specific instructions for synthesis
            
        Returns:
            Generated markdown string
        """
        # Format slides for input
        slide_text = "\n\n".join([
            f"--- Slide {s['id']} ---\n{s['text']}"
            for s in slides
        ])
        
        # Call DSPy
        result = self.generate(
            slide_content=slide_text,
            instruction=instruction
        )
        
        return result.markdown_content
