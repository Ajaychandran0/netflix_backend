from app.constants.processing import ProcessingEvent

from app.schemas.events.processing import (
    VideoProcessingStartedEvent,
    VideoProcessingStageChangedEvent,
    VideoProcessingCompletedEvent,
    VideoProcessingFailedEvent
)

from app.services.video_service import VideoService


class VideoEventHandler:

    def __init__(self, db):
        self.video_service = VideoService(db)

        self.handlers = {
            ProcessingEvent.PROCESSING_STARTED: (
                VideoProcessingStartedEvent,
                self.handle_processing_started
            ),
            ProcessingEvent.STAGE_CHANGED: (
                VideoProcessingStageChangedEvent,
                self.handle_stage_changed
            ),
            ProcessingEvent.PROCESSING_COMPLETED: (
                VideoProcessingCompletedEvent,
                self.handle_processing_completed
            ),
            ProcessingEvent.PROCESSING_FAILED: (
                VideoProcessingFailedEvent,
                self.handle_processing_failed
            ),
        }
        
    async def handle(
        self,
        payload: dict
    ) -> None:
        """
        Route an incoming processing event to its handler.
        """
        event_type = ProcessingEvent(payload["event_type"])

        event_schema, handler = self.handlers.get(event_type)
        event = event_schema.model_validate(payload)

        if handler is None:
            raise ValueError(f"Unknown event: {event_type}")

        await handler(event)

    async def handle_processing_started(
        self,
        event: VideoProcessingStartedEvent
    ) -> None:

        await self.video_service.mark_processing_started(event)

    async def handle_stage_changed(
        self,
        event: VideoProcessingStageChangedEvent
    ) -> None:

        await self.video_service.update_processing_stage(event)

    async def handle_processing_completed(
        self,
        event: VideoProcessingCompletedEvent
    ) -> None:

        await self.video_service.mark_processing_completed(event)

    async def handle_processing_failed(
        self,
        event: VideoProcessingFailedEvent
        ) -> None:

        await self.video_service.mark_processing_failed(event)