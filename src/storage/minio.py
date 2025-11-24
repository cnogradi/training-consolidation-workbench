import os
import io
from datetime import timedelta
from minio import Minio
from minio.error import S3Error

class MinioClient:
    def __init__(self, endpoint=None, access_key=None, secret_key=None, secure=False):
        self.endpoint = endpoint or os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = access_key or os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = secret_key or os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.secure = secure
        
        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )

    def ensure_bucket(self, bucket_name: str):
        """Check if bucket exists, otherwise create it."""
        if not self.client.bucket_exists(bucket_name=bucket_name):
            self.client.make_bucket(bucket_name=bucket_name)
            print(f"Bucket '{bucket_name}' created.")
        else:
            print(f"Bucket '{bucket_name}' already exists.")

    def upload_file(self, bucket_name: str, object_name: str, file_path: str, content_type: str = None):
        """Upload a file from the local filesystem."""
        self.ensure_bucket(bucket_name)
        try:
            self.client.fput_object(bucket_name=bucket_name, object_name=object_name, file_path=file_path, content_type=content_type)
            print(f"'{file_path}' is successfully uploaded as object '{object_name}' to bucket '{bucket_name}'.")
            return f"http://{self.endpoint}/{bucket_name}/{object_name}" 
        except S3Error as exc:
            print("error occurred.", exc)
            raise

    def upload_bytes(self, bucket_name: str, object_name: str, data: bytes, content_type: str = "application/octet-stream"):
        """Upload bytes data."""
        self.ensure_bucket(bucket_name)
        try:
            data_stream = io.BytesIO(data)
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=data_stream,
                length=len(data),
                content_type=content_type
            )
            print(f"Bytes uploaded as object '{object_name}' to bucket '{bucket_name}'.")
            return f"http://{self.endpoint}/{bucket_name}/{object_name}"
        except S3Error as exc:
            print("error occurred.", exc)
            raise

    def download_file(self, bucket_name: str, object_name: str, file_path: str):
        """Download a file from the bucket to the local filesystem."""
        try:
            self.client.fget_object(bucket_name=bucket_name, object_name=object_name, file_path=file_path)
            print(f"Downloaded object '{object_name}' from bucket '{bucket_name}' to '{file_path}'.")
        except S3Error as exc:
            print("error occurred.", exc)
            raise
    
    def list_objects(self, bucket_name: str, prefix: str = None, recursive: bool = False):
        """List objects in a bucket."""
        try:
            return self.client.list_objects(bucket_name=bucket_name, prefix=prefix, recursive=recursive)
        except S3Error as exc:
            print("error occurred.", exc)
            raise
        except S3Error as exc:
            print("error occurred.", exc)
            return None
