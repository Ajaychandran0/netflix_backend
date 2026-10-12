from datetime import datetime

from pydantic import BaseModel


class PlaybackResponse(BaseModel):
    playback_url: str

    expires_at: datetime