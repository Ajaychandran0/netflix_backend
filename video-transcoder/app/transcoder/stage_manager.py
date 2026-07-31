from uuid import UUID

from app.constants.processing_stage import ProcessingStage
from app.schemas.video_events import StageChangedEvent
from app.services.video.video_event_publisher import VideoEventPublisher
from app.transcoder.status_tracker import StatusTracker
from app.transcoder.progress_utils import get_stage_progress_range


class StageManager:
    """
    Coordinates stage transitions during the transcoding workflow.

    Responsibilities:
    - Update the runtime processing stage in Redis.
    - Update the runtime progress percentage.
    - Publish a PROCESSING_STAGE_CHANGED domain event.

    This class intentionally does NOT contain any transcoding logic.
    """

    def __init__(
        self,
        video_id: UUID,
        tracker: StatusTracker,
        publisher: VideoEventPublisher,
    ):
        self.video_id = video_id
        self.tracker = tracker
        self.publisher = publisher

    async def transition_to(
        self,
        stage: ProcessingStage,
    ) -> None:
        """
        Transition the video processing pipeline to a new stage.
        """

        progress = get_stage_progress_range(stage).start
        
        await self.tracker.update_stage(stage)
        await self.tracker.update_progress(progress)

        self.publisher.publish_stage_changed(
            StageChangedEvent(
                video_id=self.video_id,
                current_stage=stage,
            )
        )