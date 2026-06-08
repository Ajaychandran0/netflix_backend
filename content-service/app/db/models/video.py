import uuid
from sqlalchemy import String, Text, Enum, Integer, BigInteger, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class VideoStatus(str, enum.Enum):
    UPLOADING = "UPLOADING"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(Enum(VideoStatus), nullable=False, default=VideoStatus.UPLOADING)
    upload_path = Column(String, nullable=True)
    master_playlist_key = Column(String, nullable=True)
    thumbnail_object_key = Column(String, nullable=True)
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


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
