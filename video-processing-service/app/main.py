import asyncio

from platform_messaging import StreamConsumer

from app.core.config import settings
from app.core.logger import configure_logging, logger

from app.handlers.video_uploaded import handle

configure_logging()

async def main() -> None:
    logger.info("Starting video-processing-service")

    consumer = StreamConsumer(
        redis_url=settings.REDIS_URL,
        stream_name=settings.VIDEO_PROCESSING_STREAM,
        group_name=settings.REDIS_CONSUMER_GROUP,
        consumer_name=settings.REDIS_CONSUMER_NAME,
        message_handler=handle,
        max_concurrent_tasks=5,
        max_retries=3
    )
    
    try:
        await consumer.start()
    
    except Exception:
        logger.exception("Unhandled error in video processor service")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully")
