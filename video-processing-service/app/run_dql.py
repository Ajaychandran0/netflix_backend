import asyncio
import logging
from app.consumer.dql_processor import DLQProcessor

logging.basicConfig(level=logging.INFO)

async def main():
    redis_url = "redis://localhost:6379"
    dlq_stream = "video:stream:dlq"
    processor = DLQProcessor(redis_url=redis_url, dlq_stream=dlq_stream)
    await processor.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("DLQ processor stopped.")
