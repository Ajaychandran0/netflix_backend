from app.services.video.video_service import VideoService

class VideoEventHandler:

    def __init__(self, db):
        self.video_service = VideoService(db)

        self.handlers = {
            "VIDEO_PROCESSING_STARTED": self.handle_processing_started,
            "VIDEO_STAGE_CHANGED": self.handle_stage_changed,
            "VIDEO_PROCESSING_COMPLETED": self.handle_processing_completed,
            "VIDEO_PROCESSING_FAILED": self.handle_processing_failed,
        }

    async def handle(self, payload: dict):

        event_type = payload["event_type"]

        handler = self.handlers.get(event_type)

        if handler is None:
            raise ValueError(f"Unknown event: {event_type}")

        await handler(payload)

    async def handle_processing_started(self, payload: dict):

        await self.video_service.mark_processing_started(
            video_id=payload["video_id"],
        )

    async def handle_stage_changed(self, payload: dict):

        await self.video_service.update_processing_stage(
            video_id=payload["video_id"],
            current_stage=payload["current_stage"],
        )

    async def handle_processing_completed(self, payload: dict):

        await self.video_service.mark_processing_completed(
            video_id=payload["video_id"],
            master_playlist_key=payload["master_playlist_key"],
            thumbnail_object_key=payload["thumbnail_object_key"],
            duration_ms=int(payload["duration_ms"]),
            source_width=int(payload["source_width"]),
            source_height=int(payload["source_height"]),
        )

    async def handle_processing_failed(self, payload: dict):

        await self.video_service.mark_processing_failed(
            video_id=payload["video_id"],
            current_stage=payload["current_stage"],
            error=payload["error"],
        )