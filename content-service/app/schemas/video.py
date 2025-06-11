from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime
from enum import Enum

class VideoStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    user_id: UUID

class VideoCreate(VideoBase):
    pass  # Same fields as VideoBase

class VideoOut(VideoBase):
    id: UUID
    status: VideoStatus
    upload_path: Optional[str]
    hls_playlist_url: Optional[str]
    thumbnail_url: Optional[str]
    duration: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
