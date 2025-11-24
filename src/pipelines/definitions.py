from dagster import Definitions, load_assets_from_modules
from src.ingestion import assets as ingestion_assets
from src.storage.dagster_resources import MinioResource

all_assets = load_assets_from_modules([ingestion_assets])

defs = Definitions(
    assets=all_assets,
    resources={
        "minio": MinioResource()
    },
)
