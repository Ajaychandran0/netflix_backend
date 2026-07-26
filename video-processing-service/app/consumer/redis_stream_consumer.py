import asyncio
import logging
from app.schemas.video_event import VideoUploadEvent
from app.processor.container_launcher import launch_transcoder_container
from platform_messaging import StreamConsumer

logger = logging.getLogger(__name__)

async def message_handler(msg_id, msg_data):
    event = VideoUploadEvent(**msg_data)   
                 
    logger.info(f"Processing video_id={event.video_id} from message ID {msg_id}")                
    launch_transcoder_container(event)
    

async def run_consumer(redis_url, stream_name, group_name, consumer_name):
    consumer = StreamConsumer(
        redis_url=redis_url,
        stream_name=stream_name,
        group_name=group_name,
        consumer_name=consumer_name,
        message_handler=message_handler,
        max_concurrent_tasks=5,
        max_retries=3
    )
    await consumer.ensure_consumer_group()

    while True:
        messages = await consumer.read()
        for msg_id, msg_data in messages:
            print(f"Received message ID {msg_id} with data: {msg_data} xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            asyncio.create_task(consumer.handle(msg_id, msg_data))


