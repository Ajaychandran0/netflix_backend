import uuid

from sqlalchemy import String, Column, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.models.base import BaseModel
from app.constants.upload import UploadStatus


class UploadSession(BaseModel):
    __tablename__ = "upload_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    video_id = Column(
        UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(UUID(as_uuid=True), nullable=False)
    upload_id = Column(String, nullable=False, unique=True)  # S3/MinIO UploadId
    upload_path = Column(String, nullable=False)
    part_size = Column(Integer, nullable=False)  # e.g. 5MB
    parts_uploaded = Column(JSONB, default=list)  # list of {part_number, etag}
    total_parts = Column(Integer, nullable=False)
    parts_issued = Column(Integer, default=0)     # how many presigned parts generated so far
    status = Column(Enum(UploadStatus), default=UploadStatus.INITIATED, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # For cleanup job
    upload_completed_at = Column(DateTime(timezone=True), nullable=True)