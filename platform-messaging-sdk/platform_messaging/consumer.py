import asyncio
import logging
from typing import Awaitable, Callable

import redis.asyncio as redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class StreamConsumer:
    def __init__(
        self,
        redis_url: str,
        stream_name: str,
        group_name: str,
        consumer_name: str,
        message_handler: Callable[[str, dict], Awaitable[None]],
        *,
        max_concurrent_tasks: int = 5,
        block_timeout: int = 5000,
        max_retries: int = 3,
        dlq_stream: str | None = None,
    ):
        self.redis = redis.from_url(redis_url, decode_responses=True)

        self.stream_name = stream_name
        self.group_name = group_name
        self.consumer_name = consumer_name

        self.block_timeout = block_timeout
        self.max_retries = max_retries
        self.dlq_stream = dlq_stream or f"{stream_name}:dlq"

        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

        self.message_handler = message_handler

    # Create the consumer group if it doesn't exist
    async def ensure_consumer_group(self):
        try:
            await self.redis.xgroup_create(
                name=self.stream_name,
                groupname=self.group_name,
                id="0",
                mkstream=True,
            )

            logger.info(
                "Created consumer group '%s' on stream '%s'",
                self.group_name,
                self.stream_name,
            )

        except RedisError as e:
            if "BUSYGROUP" in str(e):
                logger.info("Consumer group already exists")
            else:
                raise

    async def read(self) -> list[tuple[str, dict]]:
        try:
            entries = await self.redis.xreadgroup(
                groupname=self.group_name,
                consumername=self.consumer_name,
                streams={self.stream_name: ">"},
                count=5,
                block=self.block_timeout,
            )

            messages = []

            for _, stream_entries in entries:
                for msg_id, msg_data in stream_entries:
                    messages.append((msg_id, msg_data))

            return messages

        except Exception:
            logger.exception("Failed to consume Redis stream")
            return []

    async def handle(self, msg_id: str, msg_data: dict):
        # semaphore to limit concurrent processing to max_concurrent_tasks count
        async with self.semaphore:
            try:
                await self.message_handler(msg_id, msg_data)

                await self.redis.xack(
                    self.stream_name,
                    self.group_name,
                    msg_id,
                )

                logger.info("Acknowledged message %s", msg_id)

            except Exception:
                logger.exception("Failed to process message %s", msg_id)

                await self.retry_or_dlq(msg_id, msg_data)

    async def retry_or_dlq(self, msg_id: str, msg_data: dict):
        ''' 
            1. Increment retry count
            2. Acknowledge the message/stream
            3. If max retries exceeded, send to DLQ (Dead Letter Queue)
            4. Otherwise, re-add to the stream with exponential backoff
        '''
        retries = int(msg_data.get("retries", 0)) + 1

        msg_data["retries"] = str(retries)

        await self.redis.xack(
            self.stream_name,
            self.group_name,
            msg_id,
        )

        if retries > self.max_retries:
            await self.redis.xadd(
                self.dlq_stream,
                msg_data,
            )

            logger.warning(
                "Message %s moved to DLQ after %s retries",
                msg_id,
                retries,
            )

            return

        # Exponential backoff (delay-based retries)
        backoff = 2**retries

        await asyncio.sleep(backoff)

        await self.redis.xadd(
            self.stream_name,
            msg_data,
        )

        logger.info(
            "Retrying message %s (attempt %s)",
            msg_id,
            retries,
        )

    async def start(self):
        await self.ensure_consumer_group()

        logger.info(
            "Consumer '%s' listening on '%s'",
            self.consumer_name,
            self.stream_name,
        )

        while True:
            messages = await self.read()

            for msg_id, msg_data in messages:
                asyncio.create_task(
                    self.handle(msg_id, msg_data)
                )