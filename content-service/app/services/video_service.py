from uuid import UUID
from datetime import datetime, timezone
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException

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
    UploadStatusSummary,
    VideoUpdateRequest,
)
from app.schemas.user import UserContext


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
            Video.status == VideoStatus.COMPLETED,
            Video.deleted_at.is_(None),
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

    async def update_user_video(
        self,
        *,
        video_id: UUID,
        user: UserContext,
        payload: VideoUpdateRequest,
    ):
        self._require_admin(user)
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=422, detail="At least one video field must be provided.")
        if "title" in updates:
            if updates["title"] is None or not updates["title"].strip():
                raise HTTPException(status_code=422, detail="Title cannot be empty.")
            updates["title"] = updates["title"].strip()

        video = await self._get_owned_video(video_id=video_id, user_id=user.id)
        for field, value in updates.items():
            setattr(video, field, value)
        await self.db.commit()
        await self.db.refresh(video)

        result = self._to_upload_status(video)
        return api_response(
            data=jsonable_encoder(result),
            message="Video updated successfully",
            code="UPDATE_VIDEO_SUCCESS",
        )

    async def delete_user_video(self, *, video_id: UUID, user: UserContext):
        self._require_admin(user)
        video = await self._get_owned_video(video_id=video_id, user_id=user.id)
        video.deleted_at = datetime.now(timezone.utc)
        await self.db.commit()
        return api_response(
            data={"id": str(video_id)},
            message="Video deleted successfully",
            code="DELETE_VIDEO_SUCCESS",
        )

    @staticmethod
    def _require_admin(user: UserContext) -> None:
        if user.role.upper() != "ADMIN":
            raise HTTPException(status_code=403, detail="Admin access is required.")

    async def _get_owned_video(self, *, video_id: UUID, user_id: UUID) -> Video:
        result = await self.db.execute(
            select(Video).where(
                Video.id == video_id,
                Video.user_id == user_id,
                Video.deleted_at.is_(None),
            )
        )
        video = result.scalar_one_or_none()
        if video is None:
            raise HTTPException(status_code=404, detail="Video not found.")
        return video

    @staticmethod
    def _to_upload_status(video: Video) -> UploadStatusSummary:
        return UploadStatusSummary(
            id=video.id,
            title=video.title,
            description=video.description,
            status=video.status,
            current_stage=video.current_stage,
            last_error=video.last_error,
            thumbnail_url=video.thumbnail_url,
            duration_ms=video.duration_ms,
            created_at=video.created_at,
        )

    async def list_user_uploads(self, *, user_id: UUID) -> list[UploadStatusSummary]:
        """Return every upload for its owner, including in-progress and failed jobs."""
        statement = (
            select(Video)
            .where(Video.user_id == user_id, Video.deleted_at.is_(None))
            .order_by(Video.created_at.desc())
        )
        result = await self.db.execute(statement)

        uploads = [
            UploadStatusSummary(
                id=video.id,
                title=video.title,
                description=video.description,
                status=video.status,
                current_stage=video.current_stage,
                last_error=video.last_error,
                thumbnail_url=video.thumbnail_url,
                duration_ms=video.duration_ms,
                created_at=video.created_at,
            )
            for video in result.scalars().all()
        ]

        return api_response(
            data=jsonable_encoder(uploads),
            message="Your uploads retrieved successfully",
            code="LIST_USER_UPLOADS_SUCCESS",
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
            Video.status == VideoStatus.COMPLETED,
            Video.deleted_at.is_(None),
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
