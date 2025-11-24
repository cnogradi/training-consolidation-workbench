# Verification Script for Sensor-Driven Flow
import uuid
from src.storage.minio import MinioClient

def main():
    # 1. Create a test file
    course_id = str(uuid.uuid4())
    filename = "sensor_test_doc.txt"
    content = b"Hello, this is a test document triggered by the MinIO sensor."
    
    bucket_name = "training-content"
    object_name = f"{course_id}/{filename}"
    
    print(f"Uploading test artifact to MinIO: {bucket_name}/{object_name}")
    
    # 2. Upload to MinIO
    client = MinioClient(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    client.ensure_bucket(bucket_name)
    client.upload_bytes(bucket_name, object_name, content, content_type="text/plain")
    
    print("\n--- Instructions ---")
    print("1. Start the Dagster Daemon and Webserver if not running:")
    print("   dagster dev -m src.pipelines.definitions")
    print("2. In the UI, enable the 'course_upload_sensor'.")
    print(f"3. The sensor should detect '{object_name}' and trigger 'process_course_job'.")
    print(f"4. Check MinIO for artifacts at '{course_id}/generated/'.")

if __name__ == "__main__":
    main()
