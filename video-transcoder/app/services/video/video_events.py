
from app.core.logger import logger
from app.schemas.event import VideoTranscodingCompletedEvent
from app.services.video.video_event_publisher import VideoEventsPublisher


def publish_video_completed_event(event: VideoTranscodingCompletedEvent) -> None:
    """Publishes a validated video transcoding completion event to the Redis stream."""
    publisher = VideoEventsPublisher()
    publisher.enqueue_video({
        "video_id": str(event.video_id),
        "master_playlist_key": event.master_playlist_key,
        "thumbnail_object_key": event.thumbnail_object_key,
        "duration": event.duration if event.duration is not None else None,
    })
    logger.info(f"Enqueued video completed event for video_id: {event.video_id}")