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
        # BAML calls are synchronous in the current version of baml-py unless configured otherwise
        # If using AsyncClient, we need to use asyncio.run() or await.
        # The standard `b` client is usually sync if generated as sync.
        # However, errors indicate 'coroutine' object, meaning baml generated async methods.
        # We need to await them. Since Dagster assets can be async or sync, 
        # we can wrap this in a sync helper or make the asset async.
        # For now, simpler to wrap in asyncio.run() here if the asset is synchronous.
        import asyncio
        return asyncio.run(b.ExtractOutline(document_text=truncated_text))

    def extract_concepts(self, slide_text: str) -> SlideContent:
        """
        Extract concepts and learning objectives from a single slide's text.
        """
        import asyncio
        return asyncio.run(b.ExtractConcepts(slide_text=slide_text))
