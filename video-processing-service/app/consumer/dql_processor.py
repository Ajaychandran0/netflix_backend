import asyncio
import logging
import redis.asyncio as redis

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

"""
    Enhancements for DLQ Processing
    
    1. Refactor DLQ Processor to another service
    2. Let user trigger requeue: move from DLQ to main stream
    3. Store DLQ logs in a file or database
    4. Add email/Slack alerts for urgent cases
    5. Expose a simple API to fetch failed messages
"""


class DLQProcessor:
    def __init__(self, redis_url: str, dlq_stream: str, poll_interval: int = 10):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.dlq_stream = dlq_stream
        self.poll_interval = poll_interval
        self.last_id = "0"

    async def process_dlq_message(self, msg_id: str, msg_data: dict):
        logger.warning(f"[DLQ] Unprocessed message {msg_id}: {msg_data}")
        # In production: alert to Slack, push to retry queue, or log to a file

    async def run(self):
        logger.info(f"Starting DLQ processor for stream '{self.dlq_stream}'")
        while True:
            try:
                entries = await self.redis.xread(
                    streams={self.dlq_stream: self.last_id},
                    count=10,
                    block=5000,  # block for 5 seconds
                )

                for stream_name, messages in entries:
                    for msg_id, msg_data in messages:
                        await self.process_dlq_message(msg_id, msg_data)
                        self.last_id = msg_id  # move cursor forward

                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.exception(f"Error processing DLQ: {e}")
                await asyncio.sleep(self.poll_interval)
