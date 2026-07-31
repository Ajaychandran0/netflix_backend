from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.video import Video, VideoStatus
from app.constants.processing import ProcessingStage
from app.schemas.processing_events import (
    ProcessingStartedEvent,
    StageChangedEvent,
    ProcessingCompletedEvent,
    ProcessingFailedEvent,
)


class VideoService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_video(self, video_id: UUID) -> Video:
        result = await self.db.execute(
            select(Video).where(Video.id == video_id)
        )
        video = result.scalar_one_or_none()

        if video is None:
            raise ValueError(f"Video '{video_id}' not found.")

        return video

    async def _save(self,video: Video,) -> None:
        await self.db.commit()
        # await self.db.refresh(video)
        # return video
        

    async def mark_processing_started(
        self,
        event: ProcessingStartedEvent
    ) -> None:
        video = await self._get_video(event.video_id)

        video.status = VideoStatus.PROCESSING
        video.current_stage = ProcessingStage.DOWNLOADING
        video.processing_started_at = datetime.now(timezone.utc)

        await self._save(video)
        
    async def update_processing_stage(
        self,
        event: StageChangedEvent
    ) -> None:
        video = await self._get_video(event.video_id)

        video.current_stage = event.current_stage

        await self._save(video)

    async def mark_processing_completed(
        self,
        event: ProcessingCompletedEvent
    ) -> None:
        video = await self._get_video(event.video_id)

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

        await self._save(video)

    async def mark_processing_failed(
        self,
        event: ProcessingFailedEvent
    ) -> None:
        video = await self._get_video(event.video_id)

        video.status = VideoStatus.FAILED
        video.current_stage = event.current_stage
        video.last_error = event.error
        video.retry_count = (video.retry_count or 0) + 1

        await self._save(video)