import json
from typing import List, Any, Dict
from unstructured.partition.auto import partition
from unstructured.staging.base import elements_to_json

def extract_text_and_metadata(file_path: str, extract_images: bool = False, image_output_dir: str = None) -> List[Dict[str, Any]]:
    """
    Extract text, metadata, and optionally images from a file using unstructured.io.
    Returns a list of dictionaries representing the elements.
    """
    try:
        kwargs = {
            "strategy": "hi_res",
            "infer_table_structure": True,
        }
        if extract_images and image_output_dir:
            # Capture Images (Diagrams, Clip Art, Photos) and Tables
            kwargs["extract_image_block_types"] = ["Image", "Table"]
            kwargs["extract_image_block_to_payload"] = False # Save to disk
            kwargs["extract_image_block_output_dir"] = image_output_dir

        elements = partition(filename=file_path, **kwargs)
        
        # Convert to list of dicts
        element_dicts = []
        for el in elements:
            d = el.to_dict()
            # Add image path if available in metadata
            if "image_path" in d.get("metadata", {}):
                # The metadata might contain the absolute path, we might want to normalize it or just keep it
                pass
            element_dicts.append(d)
            
        return element_dicts
    except Exception as e:
        print(f"Error extracting from {file_path}: {e}")
        raise
