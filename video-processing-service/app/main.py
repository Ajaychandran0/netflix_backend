import asyncio
import logging
from app.consumer.redis_stream_consumer import run_consumer
from app.core.config import settings
from app.core.logger import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting video-processing-service")

    try:
        await run_consumer(
            redis_url=settings.REDIS_URL,
            stream_name=settings.REDIS_STREAM_NAME,
            group_name=settings.REDIS_CONSUMER_GROUP,
            consumer_name=settings.REDIS_CONSUMER_NAME,
        )
    except Exception as e:
        logging.exception("Unhandled error in video processor service")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully")
