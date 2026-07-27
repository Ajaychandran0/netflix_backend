from platform_messaging import StreamProducer
from app.core.config import static_config

from app.schemas.video_events import (
    ProcessingStartedEvent,
    StageChangedEvent,
    ProcessingCompletedEvent,
    ProcessingFailedEvent,
)

from app.constants.event_types import VideoEventType


class VideoEventPublisher:
    def __init__(self):
        self.stream_name = static_config.video_events_stream
        self.producer = StreamProducer(static_config.redis_url)

    def _publish(self, event_type: VideoEventType, event) -> None:
        payload = {
            "event_type": event_type.value,
            **event.model_dump(mode="json"),
        }

        self.producer.publish(
            self.stream_name,
            payload,
        )

    def publish_processing_started(
        self,
        event: ProcessingStartedEvent,
    ) -> None:
        self._publish(VideoEventType.PROCESSING_STARTED, event)

    def publish_stage_changed(
        self,
        event: StageChangedEvent,
    ) -> None:
        self._publish(VideoEventType.STAGE_CHANGED, event)

    def publish_processing_completed(
        self,
        event: ProcessingCompletedEvent,
    ) -> None:
        self._publish(VideoEventType.PROCESSING_COMPLETED, event)

    def publish_processing_failed(
        self,
        event: ProcessingFailedEvent,
    ) -> None:
        self._publish(VideoEventType.PROCESSING_FAILED, event)