# NOTE: This file assumes 'baml_client' is generated and available in the path.
# If 'baml_client' is missing, you must run `baml-cli generate`.

try:
    from baml_client import b
    from baml_client.types import Outline, SlideContent
except ImportError:
    # Fallback or mock for when generation hasn't happened yet (e.g. initial setup)
    # This prevents import errors from crashing Dagster before the user can generate code.
    print("Warning: baml_client not found. Please run `baml-cli generate`.")
    class MockBaml:
        def ExtractOutline(self, text): raise NotImplementedError("BAML not generated")
        def ExtractConcepts(self, text): raise NotImplementedError("BAML not generated")
    b = MockBaml()
    Outline = None
    SlideContent = None

class LLMExtractor:
    def __init__(self):
        # BAML client is auto-initialized via the 'b' instance
        pass

    def extract_outline(self, document_text: str) -> Outline:
        """
        Extract hierarchical outline from the full document text (or TOC text).
        """
        # Truncate to avoid huge context if needed, though BAML/LLM handles it
        truncated_text = document_text[:20000] 
        return b.ExtractOutline(document_text=truncated_text)

    def extract_concepts(self, slide_text: str) -> SlideContent:
        """
        Extract concepts and learning objectives from a single slide's text.
        """
        return b.ExtractConcepts(slide_text=slide_text)
