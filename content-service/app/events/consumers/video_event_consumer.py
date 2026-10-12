from app.core.config.env import settings
from app.db.session import AsyncSessionLocal
from app.events.handlers.video_event_handler import VideoEventHandler

from platform_messaging import StreamConsumer


async def message_handler(
    msg_id: str,
    payload: dict,
):
    _ = msg_id  # msg_id is not used in this handler, but it can be useful for logging or debugging
    async with AsyncSessionLocal() as db:
        handler = VideoEventHandler(db)
        await handler.handle(payload)


async def start_video_event_consumer():
    consumer = StreamConsumer(
        redis_url=settings.REDIS_URL,
        stream_name=settings.VIDEO_EVENTS_STREAM,
        group_name=settings.REDIS_CONSUMER_GROUP,
        consumer_name=settings.REDIS_CONSUMER_NAME,
        message_handler=message_handler,
        max_concurrent_tasks=5,
        max_retries=3,
    )

    await consumer.start()