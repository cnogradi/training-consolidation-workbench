import os
import uuid
import json
import io
import shutil
import tempfile
from typing import List, Dict, Any
from dagster import asset, Output, AssetExecutionContext
from src.storage.dagster_resources import MinioResource
from src.ingestion.rendering import render_pdf_pages, render_pptx_slides
from src.ingestion.extraction import extract_text_and_metadata

# Default source directory
SOURCE_DIR = os.getenv("INGESTION_SOURCE_DIR", "data/raw")

@asset
def raw_documents(context: AssetExecutionContext, minio: MinioResource) -> List[Dict[str, Any]]:
    """
    Ingests documents from the source directory.
    Renders pages to images, extracts text (and embedded images), and uploads everything to MinIO.
    Returns a list of document manifests.
    """
    client = minio.get_client()
    client.ensure_bucket("images")
    client.ensure_bucket("text")
    client.ensure_bucket("manifests")

    if not os.path.exists(SOURCE_DIR):
        os.makedirs(SOURCE_DIR)
        context.log.info(f"Created source directory: {SOURCE_DIR}")
        return []

    processed_docs = []

    for filename in os.listdir(SOURCE_DIR):
        file_path = os.path.join(SOURCE_DIR, filename)
        if not os.path.isfile(file_path):
            continue
        
        if filename.startswith("."):
            continue

        doc_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, filename))
        context.log.info(f"Processing {filename} (UUID: {doc_uuid})")

        # 1. Render Images (Slides/Pages)
        images = []
        if filename.lower().endswith(".pdf"):
            images = render_pdf_pages(file_path)
        elif filename.lower().endswith(".pptx"):
            images = render_pptx_slides(file_path)
        
        image_urls = {}
        for i, img in enumerate(images):
            page_num = i + 1
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            object_name = f"{doc_uuid}/page_{page_num}.png"
            url = client.upload_bytes("images", object_name, img_bytes, content_type="image/png")
            image_urls[page_num] = url
            context.log.info(f"Uploaded page {page_num} image")

        # 2. Extract Text & Embedded Images
        try:
            with tempfile.TemporaryDirectory() as temp_extract_dir:
                elements = extract_text_and_metadata(
                    file_path, 
                    extract_images=True, 
                    image_output_dir=temp_extract_dir
                )
                
                # Upload extracted embedded images
                embedded_images_map = {}
                for img_filename in os.listdir(temp_extract_dir):
                    img_local_path = os.path.join(temp_extract_dir, img_filename)
                    if os.path.isfile(img_local_path):
                        object_name = f"{doc_uuid}/embedded/{img_filename}"
                        
                        # Detect content type (basic)
                        ext = os.path.splitext(img_filename)[1].lower()
                        ctype = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
                        
                        url = client.upload_file("images", object_name, img_local_path, content_type=ctype)
                        embedded_images_map[img_filename] = url
                        context.log.info(f"Uploaded embedded image: {img_filename}")

                # Update elements metadata with new image URLs
                for el in elements:
                    metadata = el.get("metadata", {})
                    image_path = metadata.get("image_path")
                    if image_path:
                        # unstructured usually saves files as figure-1.jpg, etc.
                        # We need to match the filename in embedded_images_map
                        img_filename = os.path.basename(image_path)
                        if img_filename in embedded_images_map:
                            # Add a custom field for the S3 URL
                            metadata["image_url"] = embedded_images_map[img_filename]
                            # Optionally clear the local path since it won't exist later
                            # metadata["image_path"] = None 

            text_json = json.dumps(elements, indent=2)
            client.upload_bytes("text", f"{doc_uuid}.json", text_json.encode('utf-8'), content_type="application/json")
            context.log.info(f"Uploaded text extraction for {filename}")
        except Exception as e:
            context.log.error(f"Failed to extract text from {filename}: {e}")
            elements = []
            embedded_images_map = {}

        # 3. Create Manifest
        manifest = {
            "doc_uuid": doc_uuid,
            "filename": filename,
            "page_count": len(images) if images else 0,
            "image_urls": image_urls,
            "embedded_images": embedded_images_map,
            "text_location": f"text/{doc_uuid}.json"
        }
        
        manifest_json = json.dumps(manifest, indent=2)
        client.upload_bytes("manifests", f"{doc_uuid}.json", manifest_json.encode('utf-8'), content_type="application/json")
        
        processed_docs.append(manifest)
    
    return processed_docs
