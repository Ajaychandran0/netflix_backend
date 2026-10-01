from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.env import settings
from app.core.utils.response import api_response

from app.constants.video import VideoStatus

from app.db.models.video import Video

from app.schemas.playback import PlaybackResponse


class PlaybackService:
    PLAYBACK_SESSION_TTL_SECONDS = 3600

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_playback_info(
        self,
        *,
        video_id: UUID,
    ) -> PlaybackResponse:

        # --------------------------------------------------
        # Find playable video
        # --------------------------------------------------

        result = await self.db.execute(
            select(Video).where(
                Video.id == video_id,
                Video.status == VideoStatus.COMPLETED,
                Video.deleted_at.is_(None),
            )
        )

        video = result.scalar_one_or_none()

        if video is None or video.master_playlist_key is None:
            raise ValueError(
                f"Playback is not available for video '{video_id}'."
            )

        # --------------------------------------------------
        # Generate playback URL. The MVP uses a public video bucket, so this
        # endpoint is deliberately viewable without an authenticated session.
        # --------------------------------------------------

        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=self.PLAYBACK_SESSION_TTL_SECONDS
        )

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
