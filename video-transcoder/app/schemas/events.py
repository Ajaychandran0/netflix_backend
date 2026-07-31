from pathlib import Path
from uuid import UUID
from pydantic import BaseModel


class ProcessingStartedEvent(BaseModel):
    video_id: UUID


class StageChangedEvent(BaseModel):
    video_id: UUID
    current_stage: str


class ProcessingCompletedEvent(BaseModel):
    video_id: UUID

    master_playlist_object_key: Path
    thumbnail_object_key: Path

    duration_ms: int
    source_width: int
    source_height: int
    source_file_size_bytes: int
    mime_type: str | None


class ProcessingFailedEvent(BaseModel):
    video_id: UUID

    current_stage: str
    error: str