from dagster import ConfigurableResource
from src.storage.minio import MinioClient

class MinioResource(ConfigurableResource):
    endpoint: str = "localhost:9000"
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    secure: bool = False

    def get_client(self) -> MinioClient:
        return MinioClient(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )
