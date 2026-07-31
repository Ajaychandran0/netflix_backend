from enum import StrEnum

from app.schemas.transcoding import StageProgressRange


class ProcessingStage(StrEnum):
    DOWNLOADING = "DOWNLOADING"
    EXTRACTING_METADATA = "EXTRACTING_METADATA"
    TRANSCODING = "TRANSCODING"
    GENERATING_PLAYLIST = "GENERATING_PLAYLIST"
    GENERATING_THUMBNAIL = "GENERATING_THUMBNAIL"
    UPLOADING_ASSETS = "UPLOADING_ASSETS"
    CLEANUP = "CLEANUP"
    


class ProcessingStatus(StrEnum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    

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

THUMBNAIL_CAPTURE_PERCENTAGE = 0.20