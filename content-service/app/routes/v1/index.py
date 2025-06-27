from fastapi import APIRouter, Depends, Request
from app.schemas.video import VideoURL, VideoBase
from app.schemas.video_upload import InitiateUploadRequest, InitiateUploadResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.video import create_video_with_presigned_url, initiate_upload_session


router = APIRouter()


@router.post("/request_upload", response_model=VideoURL)
async def request_video_upload(video_in: VideoBase, db: AsyncSession = Depends(get_db)):
    return await create_video_with_presigned_url(db, video_in)


@router.post("/initiate_upload", response_model=InitiateUploadResponse)
async def initiate_upload(
    payload: InitiateUploadRequest, db: AsyncSession = Depends(get_db)
):
    return await initiate_upload_session(db=db, payload=payload)


@router.post("complete_upload")
async def complete_video_upload(request: Request):
    """
    Endpoint to complete video upload.
    This endpoint can be used to finalize the upload process.
    """
    # Placeholder for future implementation
    return {"message": "Video upload completed. Further implementation needed."}


@router.post("cancel_upload")
async def cancel_video_upload(request: Request):
    """
    Endpoint to cancel video upload.
    This endpoint can be used to cancel an ongoing upload process.
    """
    # Placeholder for future implementation
    return {"message": "Video upload cancelled. Further implementation needed."}
