from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID

from app.db.session import get_db
from app.schemas.video import VideoListQuery, VideoListResponse, VideoResponse, UploadStatusSummary, VideoUpdateRequest
from app.core.middlewares.user_context import get_user_context
from app.schemas.user import UserContext

from app.services.video_service import VideoService

router = APIRouter(
    prefix="/videos",
)


@router.get("/mine", response_model=list[UploadStatusSummary])
async def list_my_uploads(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserContext, Depends(get_user_context)],
):
    service = VideoService(db)
    return await service.list_user_uploads(user_id=user.id)


@router.put("/{video_id}")
async def update_my_video(
    video_id: UUID,
    payload: VideoUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserContext, Depends(get_user_context)],
):
    service = VideoService(db)
    return await service.update_user_video(video_id=video_id, user=user, payload=payload)


@router.delete("/{video_id}")
async def delete_my_video(
    video_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserContext, Depends(get_user_context)],
):
    service = VideoService(db)
    return await service.delete_user_video(video_id=video_id, user=user)


@router.get("/", response_model=VideoListResponse)
async def list_videos(
    query: Annotated[VideoListQuery, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = VideoService(db)

    return await service.list_videos(
        query = query
    )

    
@router.get("/{video_id}/progress")
async def get_my_video_progress(
    video_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserContext, Depends(get_user_context)],
):
    service = VideoService(db)
    return await service.get_user_video_progress(
        video_id=video_id,
        user_id=user.id,
    )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = VideoService(db)

    return await service.get_video(video_id=video_id)
