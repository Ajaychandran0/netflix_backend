from fastapi import APIRouter
from app.services.storage import generate_presigned_url

router = APIRouter()

@router.get("/upload")
def get_upload_url(filename: str, content_type: str):
    url = generate_presigned_url(filename, content_type)
    return {"upload_url": url}
