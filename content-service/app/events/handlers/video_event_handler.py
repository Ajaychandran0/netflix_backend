from app.constants.processing import ProcessingEvent

from app.schemas.events.processing import (
    VideoProcessingStartedEvent,
    VideoProcessingStageChangedEvent,
    VideoProcessingCompletedEvent,
    VideoProcessingFailedEvent,
    VideoProcessingLaunchFailedEvent,
)

from app.services.processing_service import VideoProcessingService


class VideoEventHandler:

    def __init__(self, db):
        self.video_service = VideoProcessingService(db)

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
            ProcessingEvent.PROCESSING_LAUNCH_FAILED: (
                VideoProcessingLaunchFailedEvent,
                self.handle_processing_launch_failed
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
        handler_mapping = self.handlers.get(event_type)
        if handler_mapping is None:
            raise ValueError(f"Unknown event: {event_type}")

        event_schema, handler = handler_mapping
        event = event_schema.model_validate(payload)
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

    async def handle_processing_launch_failed(
        self,
        event: VideoProcessingLaunchFailedEvent,
    ) -> None:
        await self.video_service.mark_processing_launch_failed(event)
