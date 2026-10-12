import asyncio
from fastapi import FastAPI
from contextlib import suppress, asynccontextmanager

from app.core.utils.bucket_service import BucketService
from app.core.config.env import settings

from app.events.consumers.video_event_consumer import start_video_event_consumer
from app.events.outbox_dispatcher import run_outbox_dispatcher
from app.core.redis_client import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ------------------------------------------------------------------ 
    # Infrastructure initialization (local/development only) 
    # ------------------------------------------------------------------ 
    # NOTE: 
    # Bucket creation and access-policy configuration are kept here only 
    # to make the local MinIO environment self-contained. 
    # 
    # In a production environment, these resources should NOT be created 
    # or configured by the application at startup. S3 buckets, policies, 
    # permissions, lifecycle rules, encryption, and other infrastructure 
    # configuration should be provisioned and managed separately using 
    # Infrastructure as Code (e.g. Terraform / CloudFormation / Pulumi). 
    # 
    # The application should assume that the required buckets already 
    # exist and have the correct access configuration. 
    # 
    # TODO (production): 
    # Move bucket provisioning and access-policy configuration to IaC. 
    # ------------------------------------------------------------------
    
    # ✅ Startup logic: Ensure bucket exists
    
    bucket_service = BucketService()
    
    bucket_service.ensure_bucket_exists(
        settings.S3_TEMP_BUCKET
    )
    
    bucket_service.ensure_bucket_exists(
        settings.S3_VIDEO_BUCKET
    )
    
    # Public access is used temporarily because videos are not served through a CDN yet.
    # Once a CDN is configured to access a private origin, make this bucket private to improve security.
    bucket_service.make_bucket_public_read(
        settings.S3_VIDEO_BUCKET
    )
    
    bucket_service.ensure_bucket_exists(
        settings.S3_THUMBNAIL_BUCKET
    )
    
    # Thumbnail bucket is publicly readable
    bucket_service.make_bucket_public_read(
        settings.S3_THUMBNAIL_BUCKET
    )
    
    app.state.video_consumer_task = asyncio.create_task(
        start_video_event_consumer()
    )
    app.state.outbox_dispatcher_task = asyncio.create_task(
        run_outbox_dispatcher()
    )
    
    yield

    app.state.video_consumer_task.cancel()
    with suppress(asyncio.CancelledError):
        await app.state.video_consumer_task

    app.state.outbox_dispatcher_task.cancel()
    with suppress(asyncio.CancelledError):
        await app.state.outbox_dispatcher_task

    await redis_client.aclose()

    # 🔻 Shutdown logic (optional)
    # For example: clean up temporary files, close DB connections, etc.
