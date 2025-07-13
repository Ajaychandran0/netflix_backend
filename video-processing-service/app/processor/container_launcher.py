import docker
from app.core.logger import logger
from app.schemas.video_event import VideoUploadEvent
from app.core.config import settings

client = docker.from_env()

def launch_transcoder_container(event: VideoUploadEvent):
    try:
        container = client.containers.run(
            image=settings.DOCKER_TRANSCODER_IMAGE,  # This image should exist locally or be pulled from a registry
            name=f"transcoder-{event.video_id}",
            detach=True,
            auto_remove=True,
            network=settings.DOCKER_NETWORK,
            environment={
                "VIDEO_ID": str(event.video_id),
                "USER_ID": str(event.user_id),
                "UPLOAD_PATH": event.upload_path,
                "TITLE": event.title,
                "THUMBNAIL_URL": event.thumbnail_url or "",
            },
        )
        logger.info(f"Launched container {container.name} for video_id {event.video_id}")
    except Exception as e:
        logger.error(f"Failed to launch container for video {event.video_id}: {e}")
        raise e # Re-raise to handle in the consumer