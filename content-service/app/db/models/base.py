from app.db.base import Base

from app.db.models.mixins import (
    TimestampMixin,
    SoftDeleteMixin,
)


class BaseModel(
    Base,
    TimestampMixin,
    SoftDeleteMixin,
):
    __abstract__ = True