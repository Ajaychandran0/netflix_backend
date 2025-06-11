from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models to ensure they are registered with SQLAlchemy
from app.db.models.video import Video
