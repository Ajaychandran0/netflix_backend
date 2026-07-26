import asyncio
from app.consumer.redis_stream_consumer import run_consumer
from app.core.config import settings
from app.core.logger import configure_logging, logger
configure_logging()

async def main():
    logger.info("Starting video-processing-service")

    try:
        await run_consumer(
            redis_url=settings.REDIS_URL,
            stream_name=settings.VIDEO_PROCESSING_STREAM,
            group_name=settings.REDIS_CONSUMER_GROUP,
            consumer_name=settings.REDIS_CONSUMER_NAME,
        )
    except Exception as e:
        logger.exception("Unhandled error in video processor service")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully")
