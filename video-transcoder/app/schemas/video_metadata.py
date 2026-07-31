from pydantic import BaseModel

class VideoMetadata(BaseModel):
    duration_ms: int
    source_width: int
    source_height: int
    source_file_size_bytes: int
    mime_type: str | None