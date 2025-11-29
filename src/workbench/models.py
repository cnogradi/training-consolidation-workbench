from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ConceptNode(BaseModel):
    name: str
    domain: str

class SourceSlide(BaseModel):
    id: str             # {doc_uuid}_{page_index}
    s3_url: str         # Presigned URL
    text_preview: str
    concepts: List[ConceptNode]

class TargetDraftNode(BaseModel):
    id: str             # UUID
    title: str
    parent_id: Optional[str] = None
    source_refs: List[str] = [] # List of SourceSlide IDs mapped to this node
    status: str         # "empty", "drafting", "complete"
    content_markdown: Optional[str] = None

class SynthesisRequest(BaseModel):
    target_node_id: str
    tone_instruction: str

class SearchRequest(BaseModel):
    query: Optional[str] = None
    filters: Dict[str, Any] = {} # domain, origin, intent, type
