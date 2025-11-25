# Upload Generated Test Suite
import os
import uuid
from dotenv import load_dotenv
from src.storage.minio import MinioClient
from src.utils.generate_test_docs import generate_all

import json

def main():
    # 0. Load environment variables from .env
    load_dotenv()

    # 1. Generate Test Docs
    print("Generating test documents...")
    output_dir = "test_docs"
    generated_files = generate_all(output_dir)
    
    # 2. Get MinIO settings
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
    
    bucket_name = "training-content"
    
    client = MinioClient(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure
    )
    client.ensure_bucket(bucket_name)

    print(f"\nUploading to MinIO ({endpoint})...")
    
    for filename, filepath, metadata in generated_files:
        course_id = str(uuid.uuid4())
        object_name = f"{course_id}/{filename}"
        metadata_object_name = f"{course_id}/metadata.json"
        
        print(f"  - {filename} -> {bucket_name}/{object_name}")
        print(f"  - Metadata -> {bucket_name}/{metadata_object_name}")
        
        # Determine content type
        ctype = "application/octet-stream"
        if filename.endswith(".pdf"): ctype = "application/pdf"
        elif filename.endswith(".pptx"): ctype = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        elif filename.endswith(".docx"): ctype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        # Upload course file
        client.upload_file(bucket_name, object_name, filepath, content_type=ctype)
        
        # Upload metadata
        metadata_bytes = json.dumps(metadata, indent=2).encode('utf-8')
        client.upload_bytes(bucket_name, metadata_object_name, metadata_bytes, content_type="application/json")

    print("\n--- Upload Complete ---")
    print("1. Ensure Dagster is running: `dagster dev -m src.pipelines.definitions`")
    print("2. Enable 'course_upload_sensor' in the UI.")
    print("3. Watch the 'Runs' tab as 3 new jobs should be triggered.")

if __name__ == "__main__":
    main()
