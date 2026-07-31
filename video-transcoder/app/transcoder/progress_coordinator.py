from app.core.logger import logger
from app.constants.processing_stage import ProcessingStage

from app.transcoder.progress_tracker import TranscodingProgressTracker
from app.transcoder.status_tracker import StatusTracker
from app.transcoder.progress_utils import map_progress_to_stage

class TranscodingProgressCoordinator:
    """
    Coordinates transcoding progress updates.

    Responsibilities:
    - Receive per-resolution progress from the transcoder.
    - Calculate overall weighted progress.
    - Throttle Redis updates.
    - Update StatusTracker.

    It does NOT:
    - Parse FFmpeg output.
    - Publish events.
    - Handle database updates.
    """

    def __init__(
        self,
        resolutions: list[str],
        status_tracker: StatusTracker,
    ):
        self.status_tracker = status_tracker

        self.progress_tracker = (
            TranscodingProgressTracker(
                resolutions=resolutions,
            )
        )

    async def on_progress(
        self,
        resolution: str,
        percentage: float,
    ) -> None:
        """
        Receive progress from one FFmpeg process.

        Example:

            720p -> 42%
        """
        

        overall_progress = (
            self.progress_tracker.record_progress(
                resolution,
                percentage,
            )
        )
        
        if overall_progress is None:
            return

        pipeline_progress = map_progress_to_stage(
            ProcessingStage.TRANSCODING,
            overall_progress,
        )
        logger.info(
            "Overall transcoding progress: %.2f%%",
            overall_progress,
        )

        await self.status_tracker.update_progress(
            progress=round(pipeline_progress, 2),
        )