from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID

from app.db.session import get_db
from app.core.middlewares.user_context import get_user_context

from app.schemas.playback import PlaybackResponse
from app.schemas.user import UserContext

from app.services.playback_service import PlaybackService

router = APIRouter(
    prefix="/videos",
)

@router.get("/{video_id}/playback", response_model=PlaybackResponse)
async def get_playback_info(
    video_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserContext, Depends(get_user_context)],
):
    service = PlaybackService(db)

    return await service.get_playback_info(
        video_id=video_id,
        user=user,
    )
    
