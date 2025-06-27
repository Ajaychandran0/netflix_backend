import uuid
from sqlalchemy import String, Column, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base

class UploadSession(Base):
    __tablename__ = "upload_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    upload_id = Column(String, nullable=False, unique=True)  # S3/MinIO UploadId
    status = Column(String, nullable=False, default="initiated")  # initiated, in_progress, completed, aborted
    parts_uploaded = Column(JSON, nullable=True)  # Optional: store part numbers/etags
    expires_at = Column(DateTime(timezone=True), nullable=True)  # For cleanup job
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
