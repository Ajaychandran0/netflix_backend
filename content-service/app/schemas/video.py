from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.constants.video import VideoStatus


class VideoSummary(BaseModel):
    id: UUID

    title: str

    thumbnail_url: str | None

    duration_ms: int | None

    status: VideoStatus

    created_at: datetime
     
    
class VideoResponse(VideoSummary):
    description: str | None
    
    owner_id: UUID

    source_width: int | None
    source_height: int | None


class VideoListResponse(BaseModel):
    items: list[VideoSummary]

    total: int

    page: int

    page_size: int
  