from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    APP_ENV: Literal["development", "staging", "production"] = "development"
    API_DOCS_USER: str
    API_DOCS_PASS: str
    
    REDIS_URL: str = "redis://redis:6379/1"
    VIDEO_PROCESSING_STREAM: str = "video:processing:stream"

    REDIS_CONSUMER_GROUP: str = "video-processor-group"
    REDIS_CONSUMER_NAME: str = "video-processor-instance-1"
    PROCESSING_TIMEOUT: int = 60  # seconds

    DOCKER_TRANSCODER_IMAGE: str = "video-transcoder"
    DOCKER_NETWORK: str = "bridge"  # or the name of your internal network

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create a singleton settings instance
settings = Settings()
