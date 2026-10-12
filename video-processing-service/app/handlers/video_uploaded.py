from uuid import uuid5, NAMESPACE_URL

from app.core.logger import logger
from app.core.config import settings
from app.schemas.video_event import VideoUploadEvent
from app.processor.container_launcher import launch_transcoder_container
from platform_messaging import StreamProducer


MAX_LAUNCH_RETRIES = 3
_event_producer = StreamProducer(settings.REDIS_URL)


async def handle(
    msg_id: str,
    msg_data: dict
) -> None:

    """
    Process a VIDEO_UPLOADED event.
    """
    event = VideoUploadEvent(**msg_data)  

    logger.info(
        "Processing video %s (message %s)",
        event.video_id,
        msg_id,
    ) 
                 
    retries = int(msg_data.get("retries", 0))
    if retries >= MAX_LAUNCH_RETRIES:
        _event_producer.publish(
            settings.VIDEO_EVENTS_STREAM,
            {
                "event_type": "VIDEO_PROCESSING_LAUNCH_FAILED",
                "event_id": str(uuid5(NAMESPACE_URL, f"launch-failed:{event.attempt_id}")),
                "attempt_id": str(event.attempt_id),
                "event_sequence": "0",
                "video_id": str(event.video_id),
                "error": "Unable to start transcoder after repeated Docker API failures",
            },
        )
        logger.error(
            "Processing attempt %s exhausted launch retries; launch-failure event published",
            event.attempt_id,
        )
        return

    launch_transcoder_container(event)
