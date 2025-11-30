"""
DSPy module for synthesizing slide content into a consolidated markdown section.
"""
import dspy
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class GenerateSectionContent(dspy.Signature):
    """
    Synthesize content from source slides based on the user's instruction.
    
    Follow these rules:
    1. Integrate content from all provided slides.
    2. STRICTLY follow the provided instruction regarding format, length, and tone.
       - If the user asks for a "single slide", output a concise summary or bullet points fitting a single slide.
       - If the user asks for a "section", use standard markdown with headers and paragraphs.
    3. Ensure smooth transitions between topics.
    4. Do not explicitly mention "Slide 1" or "Slide 2" unless necessary for context.
    5. Output ONLY the markdown content. Do not wrap in JSON or other blocks.
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
        
        print("\n" + "="*50)
        print("DEBUG: DSPy Input - Slide Content:")
        print(slide_text)
        print("-" * 20)
        print("DEBUG: DSPy Input - Instruction:")
        print(instruction)
        print("="*50 + "\n")

        # Call DSPy
        result = self.generate(
            slide_content=slide_text,
            instruction=instruction
        )
        
        print("\n" + "="*50)
        print("DEBUG: DSPy Output:")
        print(result.markdown_content)
        print("="*50 + "\n")
        
        return result.markdown_content
