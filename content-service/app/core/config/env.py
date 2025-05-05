from pydantic_settings import BaseSettings
from typing import Literal

import sys
class Settings(BaseSettings):
    APP_ENV: Literal["development", "staging", "production"] = "development"
    API_DOCS_USER: str
    API_DOCS_PASS: str
    CONTENT_SERVICE_PORT: int = 3002

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a singleton settings instance
print("Settings module loadedxxxxxxxxxxxxxxxxxxxxxxxxxxx")
print(sys.path, "sys.pathxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


settings = Settings()
