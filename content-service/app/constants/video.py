from enum import Enum

class VideoStatus(str, Enum):
    UPLOADING = "UPLOADING"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
