from enum import Enum


class UploadStatus(str, Enum):
    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"
    FAILED = "FAILED"
