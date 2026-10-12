from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class VideoUploadEvent(BaseModel):
    video_id: UUID
    attempt_id: UUID
    user_id: UUID
    upload_path: str
    title: str
    thumbnail_object_key: Optional[str] = None
    retries: Optional[int] = Field(default=0, ge=0)
