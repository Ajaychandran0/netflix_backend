from datetime import datetime, timezone


from app.constants.transcoding import (
    TRANSCODING_WEIGHTS,
    PROGRESS_CHANGE_THRESHOLD,
    PROGRESS_UPDATE_INTERVAL_SECONDS,
)


class TranscodingProgressTracker:
    """
    Tracks progress of multiple FFmpeg transcoding jobs.

    Responsibilities:
    - Store individual resolution progress.
    - Calculate weighted overall progress.
    - Decide when a progress update should be published.

    This class does NOT:
    - Write to Redis.
    - Update database.
    - Publish events.
    """


    def __init__(
        self,
        resolutions: list[str],
    ):
        self.progress = {
            resolution: 0.0
            for resolution in resolutions
        }

        self.last_published_progress = 0.0

        self.last_publish_time = datetime.now(
            timezone.utc
        )


    def record_progress(
        self,
        resolution: str,
        percentage: float,
    ) -> float | None:
        """
        Update progress for a single resolution.

        Returns:
            Overall progress percentage if an update
            should be published.

            None means:
            Do not publish yet.
        """

        self.progress[resolution] = percentage

        overall_progress = (
            self._calculate_overall_progress()
        )


        if self._should_publish(
            overall_progress
        ):
            self.last_published_progress = (
                overall_progress
            )

            self.last_publish_time = datetime.now(
                timezone.utc
            )

            return round(
                overall_progress,
                2,
            )


        return None


    def _calculate_overall_progress(self) -> float:
        """
        Calculate weighted progress.

        Example:

        240p 100% * 5%
        720p 50%  * 25%
        1080p 20% * 45%

        returns combined progress.
        """

        total = 0.0

        for resolution, progress in self.progress.items():

            weight = TRANSCODING_WEIGHTS.get(
                resolution,
                0,
            )
            
            normalized = progress / 100
            total += normalized * weight


        return total * 100


    def _should_publish(
        self,
        current_progress: float,
    ) -> bool:
        """
        Decide whether Redis should receive
        another update.
        """
        
        if abs(current_progress - self.last_published_progress) < 1:
            return False

        progress_changed = (
            current_progress
            -
            self.last_published_progress
        )


        time_elapsed = (
            datetime.now(timezone.utc)
            -
            self.last_publish_time
        ).total_seconds()


        return (
            progress_changed >= PROGRESS_CHANGE_THRESHOLD
            or
            time_elapsed >= PROGRESS_UPDATE_INTERVAL_SECONDS
            or
            current_progress >= 100
        )