import json
from typing import List, Any, Dict
from unstructured.partition.auto import partition
from unstructured.staging.base import elements_to_json

def extract_text_and_metadata(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract text and metadata from a file using unstructured.io.
    Returns a list of dictionaries representing the elements.
    """
    try:
        elements = partition(filename=file_path)
        # Convert to list of dicts
        element_dicts = [el.to_dict() for el in elements]
        return element_dicts
    except Exception as e:
        print(f"Error extracting from {file_path}: {e}")
        raise
