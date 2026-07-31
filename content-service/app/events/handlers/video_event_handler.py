from app.constants.processing import ProcessingEvent

from app.schemas.processing_events import (
    ProcessingStartedEvent,
    StageChangedEvent,
    ProcessingCompletedEvent,
    ProcessingFailedEvent
)

from app.services.video.video_service import VideoService


class VideoEventHandler:

    def __init__(self, db):
        self.video_service = VideoService(db)

        self.handlers = {
            ProcessingEvent.PROCESSING_STARTED: (
                ProcessingStartedEvent,
                self.handle_processing_started
            ),
            ProcessingEvent.STAGE_CHANGED: (
                StageChangedEvent,
                self.handle_stage_changed
            ),
            ProcessingEvent.PROCESSING_COMPLETED: (
                ProcessingCompletedEvent,
                self.handle_processing_completed
            ),
            ProcessingEvent.PROCESSING_FAILED: (
                ProcessingFailedEvent,
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
        event: ProcessingStartedEvent
    ) -> None:

        await self.video_service.mark_processing_started(event)

    async def handle_stage_changed(
        self,
        event: StageChangedEvent
    ) -> None:

        await self.video_service.update_processing_stage(event)

    async def handle_processing_completed(
        self,
        event: ProcessingCompletedEvent
    ) -> None:

        await self.video_service.mark_processing_completed(event)

    async def handle_processing_failed(
        self,
        event: ProcessingFailedEvent
        ) -> None:

        await self.video_service.mark_processing_failed(event)