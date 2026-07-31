from app.constants.processing_stage import (
    ProcessingStage,
)

from app.schemas.stage_progress import (
    StageProgressRange,
)


PROCESSING_STAGE_PROGRESS = {
    ProcessingStage.DOWNLOADING: StageProgressRange(
        start=1,
        end=5,
    ),
    
    ProcessingStage.EXTRACTING_METADATA: StageProgressRange(
        start=5,
        end=10,
    ),

    ProcessingStage.TRANSCODING: StageProgressRange(
        start=10,
        end=85,
    ),

    ProcessingStage.GENERATING_PLAYLIST: StageProgressRange(
        start=85,
        end=90,
    ),

    ProcessingStage.GENERATING_THUMBNAIL: StageProgressRange(
        start=90,
        end=93,
    ),

    ProcessingStage.UPLOADING_ASSETS: StageProgressRange(
        start=93,
        end=98,
    ),

    ProcessingStage.CLEANUP: StageProgressRange(
        start=98,
        end=100,
    ),
}