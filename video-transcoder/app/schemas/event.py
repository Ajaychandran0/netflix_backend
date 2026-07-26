from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID


class VideoTranscodingCompletedEvent(BaseModel):
    video_id: UUID
    master_playlist_key: str
    thumbnail_object_key: Optional[str] = None
    duration: Optional[float] = None
    
    # event_type: str = Field(
    #     default="video.transcoding.completed",
    #     description="Event name used by consumers to identify completed transcoding events.",
    # )
    # video_id: str
    # user_id: str
    # title: str
    # upload_path: str
    # source_thumbnail_object_key: Optional[str] = None
    # output_bucket: str
    # output_base_path: str
    # master_playlist_key: str
    # master_playlist_url: HttpUrl
    # thumbnail_object_key: str
    # thumbnail_url: HttpUrl
    # resolutions: List[str]
    # output_map: Dict[str, HttpUrl]
    # status: str
    # duration_seconds: Optional[float] = None
    # transcoding_started_at: Optional[datetime] = None
    # transcoding_completed_at: Optional[datetime] = None

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "video_id": "1234-uuid",
    #             "user_id": "5678-uuid",
    #             "title": "my-video.mp4",
    #             "upload_path": "uploads/my-video.mp4",
    #             "source_thumbnail_object_key": "thumbnails/source.jpg",
    #             "output_bucket": "video-bucket",
    #             "output_base_path": "transcoded_videos/1234-uuid",
    #             "master_playlist_key": "transcoded_videos/1234-uuid/master.m3u8",
    #             "master_playlist_url": "http://minio:9000/video-bucket/transcoded_videos/1234-uuid/master.m3u8",
    #             "thumbnail_object_key": "transcoded_videos/1234-uuid/thumbnail.jpg",
    #             "thumbnail_url": "http://minio:9000/video-bucket/transcoded_videos/1234-uuid/thumbnail.jpg",
    #             "resolutions": ["240p", "360p", "480p"],
    #             "output_map": {
    #                 "240p": "http://minio:9000/video-bucket/transcoded_videos/1234-uuid/240p/index.m3u8",
    #                 "360p": "http://minio:9000/video-bucket/transcoded_videos/1234-uuid/360p/index.m3u8",
    #             },
    #             "status": "COMPLETED",
    #             "duration_seconds": 43.2,
    #             "transcoding_started_at": "2026-07-25T12:34:56Z",
    #             "transcoding_completed_at": "2026-07-25T12:35:56Z",
    #         }
    #     }
