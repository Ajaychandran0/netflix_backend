import logging
from app.schemas.video_transcoded import VideoTranscodingCompletedEvent
from app.core.config.env import settings
from platform_messaging import StreamConsumer
# from app.services.video.upload import update_video_after_processing
# from sqlalchemy.ext.asyncio import AsyncSession
# from fastapi import Depends
# from app.db.session import get_db

logger = logging.getLogger(__name__)

async def message_handler(msg_id, msg_data):
    event = VideoTranscodingCompletedEvent(**msg_data)   
    logger.info(f"Transcoded video details in content service: video_id={event.video_id} from message ID {msg_id}")  
    
    # db: AsyncSession = Depends(get_db),
    # await update_video_after_processing(db, event)              
    

async def run_video_event_consumer():
    consumer = StreamConsumer(
        redis_url=settings.REDIS_URL,
        stream_name=settings.VIDEO_EVENTS_STREAM,
        group_name=settings.REDIS_CONSUMER_GROUP,
        consumer_name=settings.REDIS_CONSUMER_NAME,
        message_handler=message_handler,
        max_concurrent_tasks=5,
        max_retries=3
    )
    
    await consumer.start()