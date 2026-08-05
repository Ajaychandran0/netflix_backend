from uuid import UUID
from pydantic import BaseModel, Field


class PresignedPart(BaseModel):
    part_number: int
    presigned_url: str
    
  
class InitiateUploadRequest(BaseModel):
    filename: str = Field(..., example="testfile.mp4")
    title: str = Field(..., example="Sample Video")
    description: str | None = Field(None, example="Test upload")
    total_parts: int = Field(..., gt=0, example=5)

class InitiateUploadResponse(BaseModel):
    upload_id: str
    video_id: UUID
    parts: list[PresignedPart]


class PartETag(BaseModel):
    part_number: int
    etag: str


class CompleteUploadRequest(BaseModel):
    video_id: UUID
    upload_id: str
    parts: list[PartETag]
    
class CompleteUploadResponse(BaseModel):
    video_id: UUID
    upload_id: str