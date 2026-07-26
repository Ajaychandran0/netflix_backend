from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime
from enum import Enum

class VideoStatus(str, Enum):
    UPLOADING = "UPLOADING"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    user_id: UUID

class VideoCreate(VideoBase):
    pass  # Same fields as VideoBase

class VideoURL(VideoCreate):
    id: UUID
    presigned_url: Optional[str]
    upload_path: Optional[str]
    status: VideoStatus
    created_at: datetime
    updated_at: Optional[datetime]

class VideoOut(VideoURL):
    hls_playlist_url: Optional[str]
    thumbnail_object_key: Optional[str]
    duration: Optional[float]

    class Config:
        orm_mode = True
