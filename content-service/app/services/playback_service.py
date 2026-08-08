from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.env import settings
from app.core.utils.response import api_response

from app.constants.playback import PlaybackSessionStatus
from app.constants.video import VideoStatus

from app.db.models.video import Video
from app.db.models.playback_session import PlaybackSession

from app.schemas.playback import PlaybackResponse
from app.schemas.user import UserContext


class PlaybackService:
    PLAYBACK_SESSION_TTL_SECONDS = 3600

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_playback_info(
        self,
        *,
        video_id: UUID,
        user: UserContext,
    ) -> PlaybackResponse:

        # --------------------------------------------------
        # Find playable video
        # --------------------------------------------------

        result = await self.db.execute(
            select(Video).where(
                Video.id == video_id,
                Video.status == VideoStatus.COMPLETED,
            )
        )

        video = result.scalar_one_or_none()

        if video is None or video.master_playlist_key is None:
            raise ValueError(
                f"Playback is not available for video '{video_id}'."
            )

        # --------------------------------------------------
        # Create playback session
        # --------------------------------------------------

        now = datetime.now(timezone.utc)

        expires_at = (
            now +
            timedelta(seconds=self.PLAYBACK_SESSION_TTL_SECONDS)
        )

        playback_session = PlaybackSession(
            user_id=user.id,
            video_id=video.id,
            status=PlaybackSessionStatus.ACTIVE,
            expires_at=expires_at,
            last_accessed_at=now,
        )

        self.db.add(playback_session)

        await self.db.commit()

        # --------------------------------------------------
        # Generate playback URL
        # --------------------------------------------------

        playback_url = (
            f"{settings.PUBLIC_VIDEO_BASE_URL}/"
            f"{video.master_playlist_key}"
        )

        response = PlaybackResponse(
            playback_url=playback_url,
            expires_at=expires_at,
        )

        return api_response(
            data=jsonable_encoder(response),
            message="Playback info retrieved successfully",
            code="PLAYBACK_INFO_RETRIEVED",
        )