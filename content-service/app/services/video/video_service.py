from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.video import Video, VideoStatus


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

    async def mark_processing_started(self, video_id: UUID) -> Video:
        video = await self._get_video(video_id)

        video.status = VideoStatus.PROCESSING
        video.current_stage = "DOWNLOADING"
        video.processing_started_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(video)

        return video

    async def update_processing_stage(
        self,
        video_id: UUID,
        current_stage: str,
    ) -> Video:
        video = await self._get_video(video_id)

        video.current_stage = current_stage

        await self.db.commit()
        await self.db.refresh(video)

        return video

    async def mark_processing_completed(
        self,
        video_id: UUID,
        master_playlist_key: str,
        thumbnail_object_key: str,
        duration_ms: int,
        source_width: int,
        source_height: int,
    ) -> Video:
        video = await self._get_video(video_id)

        video.status = VideoStatus.COMPLETED
        video.current_stage = None

        video.master_playlist_key = master_playlist_key
        video.thumbnail_object_key = thumbnail_object_key
        video.duration_ms = duration_ms
        video.source_width = source_width
        video.source_height = source_height

        video.processing_completed_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(video)

        return video

    async def mark_processing_failed(
        self,
        video_id: UUID,
        current_stage: str,
        error: str,
    ) -> Video:
        video = await self._get_video(video_id)

        video.status = VideoStatus.FAILED
        video.current_stage = current_stage
        video.last_error = error
        video.retry_count = (video.retry_count or 0) + 1

        await self.db.commit()
        await self.db.refresh(video)

        return video