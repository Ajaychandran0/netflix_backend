from uuid import UUID
from pydantic import BaseModel

from app.constants.processing import ProcessingStage


class ProcessingStartedEvent(BaseModel):
    video_id: UUID


class StageChangedEvent(BaseModel):
    video_id: UUID
    current_stage: ProcessingStage


class ProcessingCompletedEvent(BaseModel):
    video_id: UUID

    master_playlist_object_key: str
    thumbnail_object_key: str

    duration_ms: int
    source_width: int
    source_height: int
    source_file_size_bytes: int
    mime_type: str | None


class ProcessingFailedEvent(BaseModel):
    video_id: UUID

    current_stage: ProcessingStage
    error: str