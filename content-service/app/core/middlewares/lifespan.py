import asyncio
import contextlib

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.utils.bucket_service import BucketService
from app.events.consumers.video_event_consumer import start_video_event_consumer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ Startup logic: Ensure bucket exists
    bucket_service = BucketService()
    bucket_service.ensure_bucket_exists()
    
    app.state.video_consumer_task = asyncio.create_task(start_video_event_consumer())
    yield

    app.state.video_consumer_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await app.state.video_consumer_task

    # 🔻 Shutdown logic (optional)
    # For example: clean up temporary files, close DB connections, etc.