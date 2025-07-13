from pydantic import BaseModel, UUID4, Field
from typing import Optional


class VideoUploadEvent(BaseModel):
    video_id: UUID4
    user_id: UUID4
    upload_path: str
    title: str
    thumbnail_url: Optional[str] = None
    retries: Optional[int] = Field(default=0, ge=0)
