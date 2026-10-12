from datetime import datetime, timezone
from uuid import uuid4

from botocore.exceptions import ClientError
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.env import settings
from app.core.utils.response import api_response
from app.core.utils.s3_services import S3UploadService
from app.db.models.outbox_event import OutboxEvent
from app.db.models.upload_session import UploadSession, UploadStatus
from app.db.models.video import Video, VideoStatus
from app.schemas.upload import (
    CompleteUploadRequest,
    CompleteUploadResponse,
    InitiateUploadRequest,
    InitiateUploadResponse,
)
from app.schemas.user import UserContext


class UploadService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def initiate_upload_session(
        self,
        *,
        payload: InitiateUploadRequest,
        user: UserContext,
    ) -> InitiateUploadResponse:
        s3 = S3UploadService()
        object_key = f"uploads/{uuid4()}_{payload.filename}"

        # Step 1: Create multipart upload and get UploadId
        upload_id = s3.initiate_multipart_upload(object_key)

        # Step 2: Generate presigned URLs for each part
        urls = s3.generate_presigned_urls(
            object_name=object_key,
            upload_id=upload_id,
            total_parts=payload.total_parts,
        )
        # Step 3: Insert into UploadSession + Video tables
        video = Video(
            title=payload.title,
            description=payload.description,
            user_id=user.id,
            status=VideoStatus.UPLOADING,
            upload_path=object_key,
            original_filename=payload.filename,
        )
        self.db.add(video)
        await self.db.flush()

        session = UploadSession(
            video_id=video.id,
            user_id=user.id,
            upload_path=object_key,
            part_size=5 * 1024 * 1024,
            total_parts=payload.total_parts,
            status=UploadStatus.INITIATED,
            upload_id=upload_id,
            parts_uploaded=[],
        )
        self.db.add(session)
        await self.db.commit()

        await self.db.refresh(video)
        await self.db.refresh(session)
        response = InitiateUploadResponse(
            upload_id=session.upload_id,
            video_id=video.id,
            parts=urls,
        )
        return api_response(
            data=jsonable_encoder(response),
            message="Upload session initiated",
            code="UPLOAD_SESSION_INITIATED",
        )


    # For completing multipart uploads
    async def complete_upload_session(
        self,
        *,
        payload: CompleteUploadRequest,
        user: UserContext,
    ) -> CompleteUploadResponse:
        # Locking serializes duplicate completion requests. Filtering by owner
        # prevents an authenticated user from completing another user's upload.
        session = await self.db.scalar(
            select(UploadSession)
            .where(
                UploadSession.upload_id == payload.upload_id,
                UploadSession.video_id == payload.video_id,
                UploadSession.user_id == user.id,
            )
            .with_for_update()
        )
        if session is None:
            raise HTTPException(status_code=404, detail="Upload session not found")

        video = await self.db.scalar(
            select(Video)
            .where(Video.id == session.video_id, Video.user_id == user.id)
            .with_for_update()
        )
        if video is None:
            raise HTTPException(status_code=404, detail="Upload session not found")
        if session.status == UploadStatus.ABORTED:
            raise HTTPException(status_code=409, detail="Upload session was aborted")
        if session.status not in {UploadStatus.INITIATED, UploadStatus.IN_PROGRESS, UploadStatus.COMPLETED}:
            raise HTTPException(status_code=409, detail="Upload session cannot be completed")

        if session.status != UploadStatus.COMPLETED and video.status != VideoStatus.UPLOADING:
            raise HTTPException(status_code=409, detail="Video is not awaiting upload completion")
        if session.status == UploadStatus.COMPLETED and video.status in {
            VideoStatus.COMPLETED,
            VideoStatus.FAILED,
        }:
            response = CompleteUploadResponse(
                video_id=payload.video_id,
                upload_id=payload.upload_id,
            )
            return api_response(
                data=jsonable_encoder(response),
                message="Upload completed successfully",
                code="UPLOAD_VIDEO_COMPLETED",
            )

        if session.status != UploadStatus.COMPLETED:
            part_numbers = [part.part_number for part in payload.parts]
            expected_parts = set(range(1, session.total_parts + 1))
            if len(part_numbers) != session.total_parts or set(part_numbers) != expected_parts:
                raise HTTPException(
                    status_code=422,
                    detail="Uploaded parts must include each session part exactly once",
                )

            s3 = S3UploadService()
            parts = [
                {"ETag": part.etag, "PartNumber": part.part_number}
                for part in sorted(payload.parts, key=lambda item: item.part_number)
            ]
            try:
                s3.complete_multipart_upload(
                    object_name=session.upload_path,
                    upload_id=session.upload_id,
                    parts=parts,
                )
            except ClientError as exc:
                # S3 can finish the upload while the API response or subsequent
                # DB commit is lost. A retry then sees NoSuchUpload; confirm the
                # final object exists before treating that as success.
                code = exc.response.get("Error", {}).get("Code")
                if code not in {"NoSuchUpload", "404", "NotFound"}:
                    raise
                if not s3.object_exists(session.upload_path):
                    raise

            session.status = UploadStatus.COMPLETED
            session.upload_completed_at = datetime.now(timezone.utc)
            video.status = VideoStatus.QUEUED
            video.processing_attempt_id = uuid4()
            video.processing_started_at = None
            video.processing_completed_at = None
            video.current_stage = None
            video.last_error = None
            video.last_processing_event_sequence = -1

        attempt_id = video.processing_attempt_id
        if attempt_id is None:
            # Covers records created before processing attempts were introduced.
            attempt_id = uuid4()
            video.processing_attempt_id = attempt_id
            video.last_processing_event_sequence = -1

        # The unique idempotency key means a repeated completion cannot create
        # a second job for the same attempt. The state change and job intent are
        # committed atomically; Redis delivery is handled by the outbox relay.
        outbox_key = f"video:{video.id}:attempt:{attempt_id}"
        existing_outbox = await self.db.scalar(
            select(OutboxEvent.id).where(OutboxEvent.idempotency_key == outbox_key)
        )
        if existing_outbox is None:
            self.db.add(
                OutboxEvent(
                    topic=settings.VIDEO_PROCESSING_STREAM,
                    idempotency_key=outbox_key,
                    payload={
                        "video_id": str(video.id),
                        "attempt_id": str(attempt_id),
                        "upload_path": video.upload_path,
                        "user_id": str(video.user_id),
                        "title": video.title,
                        "thumbnail_object_key": video.thumbnail_object_key or "",
                    },
                )
            )
        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

        response = CompleteUploadResponse(
            video_id=payload.video_id,
            upload_id=payload.upload_id,
        )
        return api_response(
            data=jsonable_encoder(response),
            message="Upload completed successfully",
            code="UPLOAD_VIDEO_COMPLETED",
        )
