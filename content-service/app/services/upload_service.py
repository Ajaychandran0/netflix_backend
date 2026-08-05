from app.schemas.user import UserContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.utils.s3_services import S3UploadService
from app.core.utils.response import api_response
from uuid import uuid4
from app.schemas.upload import (
    InitiateUploadRequest,
    InitiateUploadResponse,
    CompleteUploadRequest,
    CompleteUploadResponse,
)
from fastapi.encoders import jsonable_encoder
from app.events.publishers.video_event_publisher import VideoProcessingEventPublisher

# models
from app.db.models.video import Video, VideoStatus
from app.db.models.upload_session import UploadSession, UploadStatus


# For multipart uploads
async def initiate_upload_session(
    db: AsyncSession, payload: InitiateUploadRequest, user: UserContext
) -> InitiateUploadResponse:
    s3 = S3UploadService()
    object_key = f"uploads/{uuid4()}_{payload.filename}"

    # Step 1: Create multipart upload and get UploadId
    upload_id = s3.initiate_multipart_upload(object_key)

    # Step 2: Generate presigned URLs for each part
    urls = s3.generate_presigned_urls(
        object_name=object_key, upload_id=upload_id, total_parts=payload.total_parts
    )
    # Step 3: Insert into UploadSession + Video tables
    new_video = Video(
        title=payload.title,
        description=payload.description,
        user_id=user.id,
        status=VideoStatus.UPLOADING,
        upload_path=object_key,
        original_filename=payload.filename
    )
    db.add(new_video)
    await db.flush()  # get video.id without commit

    upload_session = UploadSession(
        video_id=new_video.id,
        user_id=user.id,
        upload_path=object_key,
        part_size=5 * 1024 * 1024,
        total_parts=payload.total_parts,
        status=UploadStatus.INITIATED,
        upload_id=upload_id,
        parts_uploaded=[],
    )
    db.add(upload_session)
    await db.commit()
    await db.refresh(new_video)
    await db.refresh(upload_session)

    result = InitiateUploadResponse(
        upload_id=upload_session.upload_id,
        video_id=new_video.id,
        parts=urls,
    )

    return api_response(
        data=jsonable_encoder(result),
        message="Upload session initiated",
        code="UPLOAD_SESSION_INITIATED",
    )


# For completing multipart uploads
async def complete_upload_session(
    db: AsyncSession, payload: CompleteUploadRequest, user: UserContext
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

    publisher = VideoProcessingEventPublisher()
    publisher.enqueue_video(
        {
            "video_id": str(video.id),
            "upload_path": video.upload_path,
            "user_id": str(video.user_id),
            "title": video.title,
            "thumbnail_object_key": video.thumbnail_object_key,
        }
    )
    print(f"Enqueued video processing event for video_id: {video.id}")

    result = CompleteUploadResponse(
        video_id=payload.video_id,
        upload_id=payload.upload_id,
    )

    return api_response(
        data=jsonable_encoder(result),
        message="Upload completed successfully",
        code="UPLOAD_VIDEO_COMPLETED",
    )
