from app.constants.processing_progress import (
    PROCESSING_STAGE_PROGRESS,
)

from app.constants.processing_stage import (
    ProcessingStage,
)


def get_stage_progress_range(
    stage: ProcessingStage,
):
    """
    Return the configured progress range
    for a processing stage.
    """

    return PROCESSING_STAGE_PROGRESS[
        stage
    ]


def map_progress_to_stage(
    stage: ProcessingStage,
    percentage: float,
) -> float:
    """
    Maps a local stage progress (0-100)
    into the overall pipeline progress.

    Example:

        TRANSCODING

        50%

        →

        47.5%
    """

    progress_range = (
        get_stage_progress_range(
            stage
        )
    )

    return (
        progress_range.start
        +
        (progress_range.end - progress_range.start)
        *
        (percentage / 100)
    )