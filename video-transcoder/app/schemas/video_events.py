from uuid import UUID
from pydantic import BaseModel


class ProcessingStartedEvent(BaseModel):
    video_id: UUID


class StageChangedEvent(BaseModel):
    video_id: UUID
    current_stage: str


class ProcessingCompletedEvent(BaseModel):
    video_id: UUID

    master_playlist_key: str
    thumbnail_object_key: str

    duration_ms: int
    source_width: int
    source_height: int


class ProcessingFailedEvent(BaseModel):
    video_id: UUID

    current_stage: str
    error: str