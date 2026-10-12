from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.constants.video import VideoStatus

class VideoListQuery(BaseModel):
    page: int = 1
    page_size: int = 20
    search: str | None = None
    status: VideoStatus | None = None


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


class UploadStatusSummary(BaseModel):
    """The status information an uploader needs while a video is in flight."""

    id: UUID
    title: str
    description: str | None
    status: VideoStatus
    current_stage: str | None
    last_error: str | None
    thumbnail_url: str | None
    duration_ms: int | None
    created_at: datetime


class VideoProgressResponse(BaseModel):
    video_id: UUID
    status: VideoStatus
    stage: str | None
    progress: int
    updated_at: datetime | None


class VideoUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
