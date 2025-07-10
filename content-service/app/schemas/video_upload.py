from pydantic import BaseModel, Field, UUID4
from typing import List

class InitiateUploadRequest(BaseModel):
    filename: str
    chunk_count: int = Field(..., gt=0)
    content_type: str = "application/octet-stream"

class PartPresignedURL(BaseModel):
    part_number: int
    url: str

class InitiateUploadResponse(BaseModel):
    upload_id: str
    key: str
    presigned_urls: List[PartPresignedURL]
    
    
'''
This code defines the schemas for initiating a multipart upload in a content service application.
It includes request and response models for handling video uploads, including details about the file,
the number of parts, and presigned URLs for each part of the upload.
'''
# app/schemas/upload.py
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class InitiateUploadRequest(BaseModel):
    filename: str = Field(..., example="testfile.mp4")
    title: str = Field(..., example="Sample Video")
    description: Optional[str] = Field(None, example="Test upload")
    total_parts: int = Field(..., gt=0, example=5)


class PresignedPart(BaseModel):
    part_number: int
    presigned_url: str


class InitiateUploadResponse(BaseModel):
    upload_id: str
    video_id: UUID
    parts: list[PresignedPart]


class PartETag(BaseModel):
    part_number: int
    etag: str

class CompleteUploadPayload(BaseModel):
    video_id: UUID4
    upload_id: str
    parts: List[PartETag]
    
class CompleteUploadResponse(BaseModel):
    video_id: UUID4
    upload_id: str