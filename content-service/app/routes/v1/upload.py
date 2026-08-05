from fastapi import APIRouter, Depends, Request
from app.schemas.user import UserContext
from app.core.middlewares.user_context import get_user_context
from app.schemas.upload import (
    InitiateUploadRequest,
    InitiateUploadResponse,
    CompleteUploadRequest,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.upload_service import (
    initiate_upload_session,
    complete_upload_session,
)


router = APIRouter()


@router.post("/initiate_upload", response_model=InitiateUploadResponse)
async def initiate_upload(
    payload: InitiateUploadRequest,
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_user_context),
):
    return await initiate_upload_session(db=db, payload=payload, user=user)


@router.post("/complete_upload")
async def complete_upload(
    payload: CompleteUploadRequest,
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_user_context),
):
    return await complete_upload_session(db=db, payload=payload, user=user)


@router.post("/cancel_upload")
async def cancel_video_upload(request: Request):
    """
    Endpoint to cancel video upload.
    This endpoint can be used to cancel an ongoing upload process.
    """
    # Placeholder for future implementation
    return {"message": "Video upload cancelled. Further implementation needed."}
