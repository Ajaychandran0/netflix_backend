import uuid

from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.db.models.base import BaseModel


class OutboxEvent(BaseModel):
    """Durable work waiting to be delivered to Redis Streams."""

    __tablename__ = "outbox_events"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_outbox_events_idempotency_key"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(String(255), nullable=False)
    idempotency_key = Column(String(255), nullable=False)
    payload = Column(JSONB, nullable=False)
    attempts = Column(Integer, nullable=False, default=0, server_default="0")
    available_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
