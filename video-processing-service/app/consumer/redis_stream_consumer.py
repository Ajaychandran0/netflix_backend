import asyncio
import logging
import redis.asyncio as redis
from redis.exceptions import RedisError
from app.schemas.video_event import VideoUploadEvent
from app.processor.container_launcher import launch_transcoder_container

logger = logging.getLogger(__name__)


class RedisStreamConsumer:
    def __init__(
        self,
        redis_url: str,
        stream_name: str,
        group_name: str,
        consumer_name: str,
        max_concurrent_tasks: int = 5,
        block_timeout: int = 5000,  # ms
        max_retries: int = 3,
        dlq_stream: str = None,
    ):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.stream_name = stream_name
        self.group_name = group_name
        self.consumer_name = consumer_name
        self.block_timeout = block_timeout
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.max_retries = max_retries
        self.dlq_stream = dlq_stream or f"{stream_name}:dlq"
        
        # TODO - Add dlq_stream consumers

    async def ensure_consumer_group(self):
        try:
            exists = await self.redis.exists(self.stream_name)
            if not exists:
                await self.redis.xadd(self.stream_name, {"init": "true"})
            await self.redis.xgroup_create(
                name=self.stream_name,
                groupname=self.group_name,
                id="0",
                mkstream=True
            )
            logger.info(f"Consumer group {self.group_name} created on stream {self.stream_name}")
        except RedisError as e:
            if "BUSYGROUP" in str(e):
                logger.info("Consumer group already exists")
            else:
                logger.exception("Error creating consumer group")

    async def read(self):
        try:
            entries = await self.redis.xreadgroup(
                groupname=self.group_name,
                consumername=self.consumer_name,
                streams={self.stream_name: '>'},
                count=5,
                block=self.block_timeout
            )

            messages = []
            for stream_name, stream_entries in entries:
                for msg_id, msg_data in stream_entries:
                    messages.append((msg_id, msg_data))

            return messages

        except Exception as e:
            logger.exception(f"Error consuming stream: {e}")
            return []

    async def handle(self, msg_id: str, msg_data: dict):
        # semaphore to limit concurrent processing to max_concurrent_tasks count
        async with self.semaphore:
            try:
                event = VideoUploadEvent(**msg_data)
                
                logger.info(f"Processing video_id={event.video_id} from message ID {msg_id}")
                
                await launch_transcoder_container(event)
                await self.redis.xack(self.stream_name, self.group_name, msg_id)
                
                logger.info(f"Acknowledged message ID {msg_id}")
                
            except Exception as e:
                logger.error(f"Error processing message {msg_id}: {e}")
                await self.retry_or_dlq(msg_id, msg_data)

    async def retry_or_dlq(self, msg_id, msg_data):
        ''' 
            1. Increment retry count
            2. Acknowledge the message/stream
            3. If max retries exceeded, send to DLQ (Dead Letter Queue)
            4. Otherwise, re-add to the stream with exponential backoff
        '''
        retries = int(msg_data.get("retries", 0)) + 1
        msg_data["retries"] = str(retries)
        await self.redis.xack(self.stream_name, self.group_name, msg_id)

        if retries > self.max_retries:
            await self.redis.xadd(self.dlq_stream, msg_data)
            logger.warning(f"Message {msg_id} sent to DLQ after {retries} retries")
        else:
            await asyncio.sleep(2 ** retries)  # Exponential backoff (delay-based retries)
            await self.redis.xadd(self.stream_name, msg_data)
            logger.info(f"Retrying message {msg_id}, attempt {retries}")


async def run_consumer(redis_url, stream_name, group_name, consumer_name):
    consumer = RedisStreamConsumer(
        redis_url=redis_url,
        stream_name=stream_name,
        group_name=group_name,
        consumer_name=consumer_name,
        max_concurrent_tasks=5,
        max_retries=3
    )
    await consumer.ensure_consumer_group()

    while True:
        messages = await consumer.read()
        for msg_id, msg_data in messages:
            asyncio.create_task(consumer.handle(msg_id, msg_data))
