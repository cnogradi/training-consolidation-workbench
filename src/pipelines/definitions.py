from dagster import Definitions, load_assets_from_modules, define_asset_job
from src.ingestion import assets as ingestion_assets
from src.ingestion.sensors import course_upload_sensor
from src.storage.dagster_resources import MinioResource

all_assets = load_assets_from_modules([ingestion_assets])

# Define the job that the sensor triggers
process_course_job = define_asset_job(
    name="process_course_job",
    selection="process_course_artifact"
)

defs = Definitions(
    assets=all_assets,
    jobs=[process_course_job],
    sensors=[course_upload_sensor],
    resources={
        "minio": MinioResource()
    },
)
