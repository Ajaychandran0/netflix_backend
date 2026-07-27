from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config.env import settings
from typing import AsyncGenerator

isEcho = settings.APP_ENV != "production"
engine = create_async_engine(settings.DATABASE_URL, future=True, echo=isEcho)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session