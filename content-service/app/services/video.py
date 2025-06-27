from app.schemas.video import VideoCreate, VideoURL
from app.db.models.video import Video, VideoStatus
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.utils.s3 import generate_presigned_url
from app.core.utils.s3_services import S3UploadService
from uuid import uuid4
from app.schemas.video_upload import (
    InitiateUploadRequest,
    InitiateUploadResponse,
    PresignedPart
)
from app.db.models.upload_session import UploadSession

# For multipart uploads
async def initiate_upload_session(
    db: AsyncSession, payload: InitiateUploadRequest
) -> InitiateUploadResponse:
    s3 = S3UploadService()
    object_key = f"uploads/{uuid4()}_{payload.filename}"
    
    # Step 1: Create multipart upload and get UploadId
    upload_id = s3.initiate_multipart_upload(object_key)
    print(f"Upload ID: {upload_id}")

    # Step 2: Generate presigned URLs for each part
    urls = s3.generate_presigned_urls(object_name=object_key, upload_id=upload_id, total_parts=payload.total_parts)
    print(f"Presigned URLs: {urls}")


    # Step 3: Insert into UploadSession + Video tables
    new_video = Video(
        title=payload.filename,
        description=payload.description,
        user_id=payload.user_id,
        status=VideoStatus.UPLOADING,
        upload_path=object_key,
    )
    
    db.add(new_video)
    await db.flush()  # get video.id without commit

    upload_session = UploadSession(
        user_id=payload.user_id,
        status=VideoStatus.UPLOADING,
        upload_id=upload_id,
        video_id=new_video.id,
        parts_uploaded=payload.total_parts,
    )
    db.add(upload_session)
    await db.commit()
    await db.refresh(new_video)
    await db.refresh(upload_session)

    return InitiateUploadResponse(
        upload_id=upload_session.upload_id,
        video_id=new_video.id,
        parts=urls,
    )


# For single video uploads
async def create_video_with_presigned_url(
    db: AsyncSession, video_in: VideoCreate
) -> VideoURL:
    presigned_url = generate_presigned_url(video_in.title)

    new_video = Video(
        title=video_in.title,
        description=video_in.description,
        user_id=video_in.user_id,
        upload_path=presigned_url["upload_path"],
        status=VideoStatus.UPLOADING,
    )

    db.add(new_video)
    await db.commit()
    await db.refresh(new_video)

    return VideoURL(
        id=new_video.id,
        title=new_video.title,
        description=new_video.description,
        user_id=new_video.user_id,
        status=new_video.status,
        upload_path=presigned_url["upload_path"],
        presigned_url=presigned_url["presigned_url"],
        created_at=new_video.created_at,
        updated_at=new_video.updated_at,
    )
