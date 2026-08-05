from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.constants.processing import ProcessingStage



class BaseEvent(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    
class VideoProcessingStartedEvent(BaseEvent):
    video_id: UUID


class VideoProcessingStageChangedEvent(BaseEvent):
    video_id: UUID
    current_stage: ProcessingStage


class VideoProcessingCompletedEvent(BaseEvent):
    video_id: UUID

    master_playlist_object_key: str
    thumbnail_object_key: str

    duration_ms: int
    source_width: int
    source_height: int
    source_file_size_bytes: int
    mime_type: str | None


class VideoProcessingFailedEvent(BaseEvent):
    video_id: UUID

    current_stage: ProcessingStage
    error: str