import asyncio
import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select

from app.core.redis_client import redis_client
from app.db.models.outbox_event import OutboxEvent
from app.db.models.video import Video, VideoStatus
from app.core.config.env import settings
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


def _retry_delay(attempts: int) -> timedelta:
    return timedelta(seconds=min(2 ** min(attempts, 8), 300))


async def dispatch_outbox_batch(batch_size: int = 25) -> int:
    """Publish pending outbox rows; safely retries publish/commit ambiguity."""
    now = datetime.now(timezone.utc)
    published = 0
    async with AsyncSessionLocal() as db:
        rows = (
            await db.execute(
                select(OutboxEvent)
                .where(
                    OutboxEvent.published_at.is_(None),
                    OutboxEvent.available_at <= now,
                )
                .order_by(OutboxEvent.created_at)
                .limit(batch_size)
                .with_for_update(skip_locked=True)
            )
        ).scalars().all()

        for row in rows:
            try:
                # Redis Streams accepts scalar fields. The complete job payload
                # contains only strings, and duplicate deliveries are guarded by
                # attempt_id and deterministic container naming downstream.
                await redis_client.xadd(row.topic, row.payload)
                row.published_at = datetime.now(timezone.utc)
                row.last_error = None
                published += 1
            except Exception as exc:
                row.attempts += 1
                row.last_error = str(exc)[:4000]
                row.available_at = datetime.now(timezone.utc) + _retry_delay(row.attempts)
                logger.exception(
                    "Outbox publish failed for event %s (attempt %s)",
                    row.id,
                    row.attempts,
                )

        await db.commit()
    return published


async def reconcile_legacy_processing_rows() -> None:
    """Give pre-attempt queued jobs a new attempt and durable outbox record."""
    async with AsyncSessionLocal() as db:
        rows = (
            await db.execute(
                select(Video)
                .where(Video.status.in_([VideoStatus.QUEUED, VideoStatus.PROCESSING]))
                .with_for_update(skip_locked=True)
            )
        ).scalars().all()

        for video in rows:
            is_legacy_attempt = video.processing_attempt_id is None
            if video.processing_attempt_id is None:
                video.processing_attempt_id = uuid4()
                video.last_processing_event_sequence = -1
            # PROCESSING rows from before attempt IDs cannot accept their old
            # worker events. Requeue only those legacy rows; never reset an
            # active attempt during a content-service restart.
            if video.status == VideoStatus.PROCESSING and is_legacy_attempt:
                video.status = VideoStatus.QUEUED
                video.current_stage = None
                video.processing_started_at = None
                video.processing_completed_at = None

            attempt_id = video.processing_attempt_id
            key = f"video:{video.id}:attempt:{attempt_id}"
            exists = await db.scalar(
                select(OutboxEvent.id).where(OutboxEvent.idempotency_key == key)
            )
            if exists is None:
                db.add(
                    OutboxEvent(
                        topic=settings.VIDEO_PROCESSING_STREAM,
                        idempotency_key=key,
                        payload={
                            "video_id": str(video.id),
                            "attempt_id": str(attempt_id),
                            "upload_path": video.upload_path,
                            "user_id": str(video.user_id),
                            "title": video.title,
                            "thumbnail_object_key": video.thumbnail_object_key or "",
                        },
                    )
                )
        await db.commit()


async def run_outbox_dispatcher(poll_interval_seconds: float = 1.0) -> None:
    logger.info("Starting transactional outbox dispatcher")
    reconciled = False
    while True:
        try:
            if not reconciled:
                await reconcile_legacy_processing_rows()
                reconciled = True
            dispatched = await dispatch_outbox_batch()
            if dispatched == 0:
                await asyncio.sleep(poll_interval_seconds)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Outbox dispatcher iteration failed")
            await asyncio.sleep(poll_interval_seconds)
