from app.core.logger import logger
from app.schemas.video_event import VideoUploadEvent
from app.processor.container_launcher import launch_transcoder_container


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
                 
    launch_transcoder_container(event)
    