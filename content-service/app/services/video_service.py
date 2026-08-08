from uuid import UUID
from fastapi.encoders import jsonable_encoder

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.core.utils.response import api_response
from app.db.models.video import Video
from app.constants.video import VideoStatus

from app.schemas.video import (
    VideoListQuery,
    VideoListResponse,
    VideoResponse,
    VideoSummary,
)


class VideoService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_videos(
        self,
        *,
        query: VideoListQuery,
    ) -> VideoListResponse:
        total = await self._count_videos(query)
        videos = await self._get_videos(query)

        result = VideoListResponse(
            items=[
                self._to_video_summary(video)
                for video in videos
            ],
            total=total,
            page=query.page,
            page_size=query.page_size,
        )

        return api_response(
            data=jsonable_encoder(result),
            message="Videos listed successfully",
            code="LIST_VIDEOS_SUCCESS",
        )
        
    async def get_video(
        self,
        *,
        video_id: UUID,
    ) -> VideoResponse:
        statement = select(Video).where(
            Video.id == video_id,
            Video.status == VideoStatus.COMPLETED
        )

        result = await self.db.execute(statement)
        video = result.scalar_one_or_none()

        if not video:
            raise ValueError(f"Video '{video_id}' not found.")

        return api_response(
            data=jsonable_encoder(self._to_video_response(video)),
            message="Video retrieved successfully",
            code="GET_VIDEO_SUCCESS",
        )


    # Helper methods for internal use
    # --------------------------------  

    async def _count_videos(
        self,
        query: VideoListQuery,
    ) -> int:
        statement = self._build_video_query(query)

        count_query = (
            select(func.count())
            .select_from(statement.subquery())
        )

        result = await self.db.execute(count_query)

        return result.scalar_one()

    async def _get_videos(
        self,
        query: VideoListQuery,
    ) -> list[Video]:
        offset = (query.page - 1) * query.page_size

        statement = (
            self._build_video_query(query)
            .order_by(Video.created_at.desc())
            .offset(offset)
            .limit(query.page_size)
        )

        result = await self.db.execute(statement)

        return list(result.scalars().all())

    def _build_video_query(
        self,
        query: VideoListQuery,
    ) -> Select[tuple[Video]]:
        statement = select(Video).where(
            Video.status == VideoStatus.COMPLETED
        )

        if query.search:
            statement = statement.where(
                Video.title.ilike(f"%{query.search}%")
            )
            
        # Future filters
        #
        # if query.genre:
        #     statement = statement.where(
        #         Video.genre == query.genre
        #     )
        #
        # if query.language:
        #     statement = statement.where(
        #         Video.language == query.language
        #     )

        return statement

    def _to_video_summary(
        self,
        video: Video,
    ) -> VideoSummary:
        return VideoSummary(
            id=video.id,
            title=video.title,
            thumbnail_url=video.thumbnail_url,
            duration_ms=video.duration_ms,
            status=video.status,
            created_at=video.created_at,
        )

    def _to_video_response(
        self,
        video: Video,
    ) -> VideoResponse:
        return VideoResponse(
            id=video.id,
            title=video.title,
            thumbnail_url=video.thumbnail_url,
            duration_ms=video.duration_ms,
            status=video.status,
            created_at=video.created_at,
            description=video.description,
            owner_id=video.user_id,
            source_width=video.source_width,
            source_height=video.source_height,
        )