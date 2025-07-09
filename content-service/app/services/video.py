from app.schemas.video import VideoCreate, VideoURL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.utils.s3 import generate_presigned_url
from app.core.utils.s3_services import S3UploadService
from uuid import uuid4
from app.schemas.video_upload import (
    InitiateUploadRequest,
    InitiateUploadResponse,
    CompleteUploadPayload,
    CompleteUploadResponse,
)

# models
from app.db.models.video import Video, VideoStatus
from app.db.models.upload_session import UploadSession, UploadStatus


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
    urls = s3.generate_presigned_urls(
        object_name=object_key, upload_id=upload_id, total_parts=payload.total_parts
    )
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
        video_id=new_video.id,
        user_id=payload.user_id,
        upload_path=object_key,
        part_size=5 * 1024 * 1024,
        total_parts=payload.total_parts,
        status=UploadStatus.INITIATED,
        upload_id=upload_id,
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


# # For completing multipart uploads
async def complete_upload_session(
    db: AsyncSession, payload: CompleteUploadPayload
) -> CompleteUploadResponse:
    # Get upload session
    result = await db.execute(
        select(UploadSession).where(
            UploadSession.upload_id == payload.upload_id,
            UploadSession.video_id == payload.video_id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise ValueError("Invalid upload session")

    # Finalize on S3
    s3 = S3UploadService()
    parts = [{"ETag": p.etag, "PartNumber": p.part_number} for p in payload.parts]

    s3.complete_multipart_upload(
        object_name=session.upload_path, upload_id=payload.upload_id, parts=parts
    )

    # Update DB
    session.status = UploadStatus.COMPLETED
    video = await db.get(Video, payload.video_id)
    if video:
        video.status = VideoStatus.COMPLETED
    await db.commit()

    return CompleteUploadResponse(
        message="Upload completed successfully",
        video_id=payload.video_id,
        upload_id=payload.upload_id,
    )
