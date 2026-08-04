import enum
import uuid

from sqlalchemy import (
    DateTime,
    Enum,
    String,
    Text,
    Column,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.models.base import BaseModel


class PlaybackSessionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


class PlaybackSession(
    BaseModel
):
    __tablename__ = "playback_sessions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    video_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    status = Column(
        Enum(PlaybackSessionStatus),
        nullable=False,
        default=PlaybackSessionStatus.ACTIVE,
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    last_accessed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    client_ip = Column(
        String(45),
        nullable=True,
    )

    user_agent = Column(
        Text,
        nullable=True,
    ) 

    __table_args__ = (
        Index("ix_playback_sessions_user_status", "user_id", "status"),
        Index("ix_playback_sessions_video_status", "video_id", "status"),
    )