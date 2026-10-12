from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.video import Video, VideoStatus
from app.schemas.events.processing import (
    VideoProcessingCompletedEvent,
    VideoProcessingFailedEvent,
    VideoProcessingLaunchFailedEvent,
    VideoProcessingStartedEvent,
    VideoProcessingStageChangedEvent,
)


class VideoProcessingService:
    """Applies attempt-scoped, ordered, idempotent processing events."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _apply_event(self, event, apply) -> None:
        video = await self.db.scalar(
            select(Video).where(Video.id == event.video_id).with_for_update()
        )
        if video is None:
            raise ValueError(f"Video '{event.video_id}' not found")

        last_sequence = video.last_processing_event_sequence
        if last_sequence is None:
            last_sequence = -1

        if (
            video.processing_attempt_id != event.attempt_id
            or event.event_sequence <= last_sequence
        ):
            await self.db.rollback()
            return

        apply(video)
        video.last_processing_event_sequence = event.event_sequence

        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

    async def mark_processing_started(self, event: VideoProcessingStartedEvent) -> None:
        def apply(video: Video) -> None:
            if video.status == VideoStatus.QUEUED:
                video.status = VideoStatus.PROCESSING
                video.processing_started_at = datetime.now(timezone.utc)
                video.processing_completed_at = None
                video.last_error = None

        await self._apply_event(event, apply)

    async def update_processing_stage(self, event: VideoProcessingStageChangedEvent) -> None:
        def apply(video: Video) -> None:
            # A stage event can arrive before the started event because different
            # consumer tasks may finish out of order. Treat it as proof of start.
            if video.status == VideoStatus.QUEUED:
                video.status = VideoStatus.PROCESSING
                video.processing_started_at = datetime.now(timezone.utc)
                video.processing_completed_at = None
                video.last_error = None
            if video.status == VideoStatus.PROCESSING:
                video.current_stage = event.current_stage

        await self._apply_event(event, apply)

    async def mark_processing_completed(self, event: VideoProcessingCompletedEvent) -> None:
        def apply(video: Video) -> None:
            # Completion may be the first event observed if earlier messages are
            # delayed; sequence ordering still makes older events harmless.
            if video.status == VideoStatus.QUEUED:
                video.processing_started_at = datetime.now(timezone.utc)

            if video.status in {VideoStatus.QUEUED, VideoStatus.PROCESSING}:
                video.status = VideoStatus.COMPLETED
                video.current_stage = None
                video.master_playlist_key = event.master_playlist_object_key
                video.thumbnail_object_key = event.thumbnail_object_key
                video.duration_ms = event.duration_ms
                video.source_width = event.source_width
                video.source_height = event.source_height
                video.source_file_size_bytes = event.source_file_size_bytes
                video.mime_type = event.mime_type
                video.processing_completed_at = datetime.now(timezone.utc)
                video.last_error = None

        await self._apply_event(event, apply)

    async def mark_processing_failed(self, event: VideoProcessingFailedEvent) -> None:
        def apply(video: Video) -> None:
            if video.status == VideoStatus.QUEUED:
                video.processing_started_at = datetime.now(timezone.utc)

            if video.status in {VideoStatus.QUEUED, VideoStatus.PROCESSING}:
                video.status = VideoStatus.FAILED
                video.current_stage = event.current_stage
                video.last_error = event.error

        await self._apply_event(event, apply)

    async def mark_processing_launch_failed(
        self,
        event: VideoProcessingLaunchFailedEvent,
    ) -> None:
        def apply(video: Video) -> None:
            # A launch failure means the transcoder never started.
            if video.status == VideoStatus.QUEUED:
                video.status = VideoStatus.FAILED
                video.current_stage = None
                video.last_error = event.error

        await self._apply_event(event, apply)
