from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID

from app.db.session import get_db
from app.schemas.video import VideoListQuery, VideoListResponse, VideoResponse

from app.services.video_service import VideoService

router = APIRouter(
    prefix="/videos",
)


@router.get("/", response_model=VideoListResponse)
async def list_videos(
    query: Annotated[VideoListQuery, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = VideoService(db)

    return await service.list_videos(
        query = query
    )
    
    
@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = VideoService(db)

    return await service.get_video(video_id=video_id)
    