from uuid import uuid4

from platform_messaging import StreamProducer
from app.core.config import static_config, dynamic_config

from app.schemas.events import (
    ProcessingStartedEvent,
    StageChangedEvent,
    ProcessingCompletedEvent,
    ProcessingFailedEvent,
)

from app.constants.events import VideoEventType


class VideoEventPublisher:
    def __init__(self):
        self.stream_name = static_config.video_events_stream
        self.producer = StreamProducer(static_config.redis_url)
        self.event_sequence = 0

    def _publish(self, event_type: VideoEventType, event) -> None:
        self.event_sequence += 1
        payload = {
            "event_type": event_type.value,
            "event_id": str(uuid4()),
            "attempt_id": dynamic_config.attempt_id,
            "event_sequence": self.event_sequence,
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
