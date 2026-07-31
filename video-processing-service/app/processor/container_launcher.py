import docker

from app.core.config import settings
from app.core.logger import logger
from app.schemas.video_event import VideoUploadEvent


client = docker.from_env()

def launch_transcoder_container(
    event: VideoUploadEvent,
) -> None:
    """
    Launch a transcoder container for the uploaded video.
    """

    container_name =  f"transcoder-{event.video_id}"

    environment = {
        "VIDEO_ID": str(event.video_id),
        "UPLOAD_PATH": event.upload_path,
    }

    try:
        client.containers.run(
            image=settings.DOCKER_TRANSCODER_IMAGE,
            name=container_name,
            detach=True,
            auto_remove=False,      # Enable in production if desired
            network=settings.DOCKER_NETWORK,
            environment=environment,
        )

        logger.info(
            "Started transcoder container '%s' for video %s",
            container_name,
            event.video_id,
        )

    except Exception:
        logger.exception(
            "Failed to launch transcoder container for video %s",
            event.video_id,
        )
        raise