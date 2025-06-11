from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    APP_ENV: Literal["development", "staging", "production"] = "development"
    API_DOCS_USER: str
    API_DOCS_PASS: str
    CONTENT_SERVICE_PORT: int = 3002
    DATABASE_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY : str
    AWS_S3_ENDPOINT :str
    AWS_REGION:str
    MINIO_TEMP_BUCKET:str

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a singleton settings instance
settings = Settings()
