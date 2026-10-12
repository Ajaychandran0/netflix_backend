import docker
from docker.errors import NotFound

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

    container_name = f"transcoder-{event.video_id}-{event.attempt_id}"

    environment = {
        "VIDEO_ID": str(event.video_id),
        "PROCESSING_ATTEMPT_ID": str(event.attempt_id),
        "UPLOAD_PATH": event.upload_path,
    }

    try:
        try:
            existing = client.containers.get(container_name)
            existing.reload()
            logger.info(
                "Processing attempt %s already has container %s (%s)",
                event.attempt_id,
                container_name,
                existing.status,
            )
            # Never start the same attempt twice. An exited worker reports its
            # terminal outcome through the event stream; recovery is a new
            # attempt with a new attempt_id.
            return
        except NotFound:
            pass

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
        # Docker may accept the create/start request even if the client loses
        # the response. Treat an existing container as an accepted launch.
        try:
            existing = client.containers.get(container_name)
            existing.reload()
            logger.warning(
                "Container %s exists after launch error (%s); treating job as accepted",
                container_name,
                existing.status,
            )
        except NotFound:
            raise
