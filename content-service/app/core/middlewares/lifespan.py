from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.utils.bucket_service import BucketService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ Startup logic: Ensure bucket exists
    bucket_service = BucketService()
    bucket_service.ensure_bucket_exists()

    yield

    # 🔻 Shutdown logic (optional)
    # For example: clean up temporary files, close DB connections, etc.