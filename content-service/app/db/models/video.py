import uuid

from sqlalchemy import String, Text, Enum, Integer, BigInteger, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.db.models.base import BaseModel
from app.constants.video import VideoStatus
from app.core.config.env import settings


class Video(BaseModel):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(Enum(VideoStatus), nullable=False, default=VideoStatus.UPLOADING)
    upload_path = Column(String, nullable=True)
    master_playlist_key = Column(String, nullable=True)
    
    thumbnail_object_key = Column(String, nullable=True)
    
    @property
    def thumbnail_url(self) -> str | None:
        if self.thumbnail_object_key is None:
            return None

        return (
            f"{settings.PUBLIC_THUMBNAIL_BASE_URL}/"
            f"{self.thumbnail_object_key}"
        )
        
    duration_ms = Column(BigInteger, nullable=True)
    source_file_size_bytes = Column(BigInteger, nullable=True)
    mime_type = Column(String(255), nullable=True)
    original_filename = Column(String(255), nullable=True)
    source_width = Column(Integer, nullable=True)
    source_height = Column(Integer, nullable=True)
    
    # currrent_stage values: downloading, transcoding, generating_thumbnails, uploading_assets, finalizing, etc. This is for more granular tracking within the PROCESSING status.
    # current_stage future possible values: validating_manifest, extracting_audio, ai_moderation, packaging_dash, uploading_subtitles, creating_preview_clips
    current_stage = Column(String, nullable=True)
    
    retry_count = Column(Integer, nullable=True)
    last_error = Column(Text, nullable=True)
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    # Identifies the currently authorized processing run. Events from an older
    # run are ignored even if they arrive after a retry has started.
    processing_attempt_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    last_processing_event_sequence = Column(Integer, nullable=False, default=-1, server_default="-1")


'''
Future tables to be added:

video_assets - to track individual assets like different resolution videos, thumbnails, subtitles, posters, etc.
------------
id
video_id
asset_type
object_key
metadata
created_at


video_processing_events - For audit/history/debugging.
-----------------------

video_id
event_type
previous_status
new_status
worker_id
metadata
created_at

'''
