from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    APP_ENV: Literal["development", "staging", "production"] = "development"
    API_DOCS_USER: str
    API_DOCS_PASS: str
    
    REDIS_URL: str
    DOCKER_NETWORK: str = "bridge"
    VIDEO_PROCESSING_STREAM: str = "video:processing:stream"
    VIDEO_EVENTS_STREAM: str = "video:events:stream"
    REDIS_CONSUMER_GROUP: str = "video-transcoder-update-group"
    REDIS_CONSUMER_NAME: str = "video-transcoder-update-instance-1"

    CONTENT_SERVICE_PORT: int = 3002
    DATABASE_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY : str
    AWS_S3_ENDPOINT :str
    AWS_S3_PUBLIC_ENDPOINT: str
    AWS_REGION:str
    S3_TEMP_BUCKET:str
    S3_VIDEO_BUCKET: str

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a singleton settings instance
settings = Settings()
