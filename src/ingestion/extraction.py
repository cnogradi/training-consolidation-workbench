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
        # Basic strategy to avoid heavy ML models if hi_res is failing to install
        # Or keep hi_res but rely on lighter models if possible.
        # If 'all-docs' is removed, hi_res might not work for complex layouts without detectron2/yolo.
        # Fallback to 'fast' or 'auto' if heavy libs are missing.
        
        strategy = "auto" # Let unstructured decide based on available libs
        
        kwargs = {
            "strategy": strategy,
            "infer_table_structure": False, # True often requires heavy models
        }
        if extract_images and image_output_dir:
            # Image extraction strictly requires hi_res and deep learning models.
            # If we are cutting deps to avoid torch/cuda, we might lose this feature.
            # We will try to request it, but if libs are missing, unstructured might raise an error or warn.
            # For now, we keep the logic but user must be aware:
            # REDUCED INSTALL -> NO IMAGE EXTRACTION from PDFs usually.
            pass
            
            # If we really want to try:
            # kwargs["strategy"] = "hi_res" 
            # kwargs["extract_image_block_types"] = ["Image", "Table"]
            # ...
            
            # Since the user asked to cut cuda/torch deps to fix install, 
            # we likely CANNOT support image extraction from PDF via Unstructured models.
            # We will disable it in this configuration to ensure pipeline runs.
            print("Warning: Image extraction disabled due to reduced dependencies.")

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
