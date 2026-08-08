from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import boto3

class StaticSettings(BaseSettings):
    # From .env file
    # AWS S3 / MinIO settings
    aws_access_key_id: str = Field(default="minioadmin", env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(
        default="minioadmin", env="AWS_SECRET_ACCESS_KEY"
    )
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_s3_endpoint: HttpUrl = Field(default="http://minio:9000", env="AWS_S3_ENDPOINT")

    s3_temp_bucket: str = Field(default="temp-bucket", env="S3_TEMP_BUCKET")
    s3_video_bucket: str = Field(default="video-bucket", env="S3_VIDEO_BUCKET")
    s3_thumbnail_bucket: str = Field(default="thumbnail-bucket", env="S3_THUMBNAIL_BUCKET")

    # Redis settings
    redis_url: str = Field(default="redis://redis:6379/1", env="REDIS_URL")
    redis_status_prefix: str = Field(default="video:status", env="REDIS_STATUS_PREFIX")

    # other settings
    video_events_stream: str = Field(default="video:events:stream", env="VIDEO_EVENTS_STREAM")

    class Config:
        env_file = ".env"
        case_sensitive = False


class DynamicSettings(BaseSettings):
    # Passed via `-e` at container runtime
    video_id: str = Field(env="VIDEO_ID")
    upload_path: str = Field(env="UPLOAD_PATH")

    class Config:
        # No .env for dynamic; only read from actual env vars
        env_file = None
        case_sensitive = False


def get_settings() -> tuple[StaticSettings, DynamicSettings]:
    try:
        static = StaticSettings()
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load static settings: {e}")

    try:
        dynamic = DynamicSettings()
    except Exception as e:
        raise RuntimeError(
            f"❌ Failed to load dynamic settings (missing required envs passed at runtime): {e}"
        )

    return static, dynamic

static_config, dynamic_config = get_settings()
    