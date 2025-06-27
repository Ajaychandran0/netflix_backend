from uuid import uuid4
from app.core.config.env import settings
from app.core.utils.s3_client import get_s3_public_client
import uuid
from typing import List
from app.schemas.video_upload import PartPresignedURL, PresignedPart

s3 = get_s3_public_client()


def initiate_multipart_upload(payload):
    object_key = f"uploads/{uuid4()}_{payload.filename}"

    # Step 1: Create multipart upload and get UploadId
    upload_id = s3.create_multipart_upload(object_key)

    # Step 2: Generate presigned URLs for each part
    urls = []
    for part_number in range(1, payload.total_parts + 1):
        url = s3.generate_presigned_url_for_part(object_key, upload_id, part_number)
        urls.append(PresignedPart(part_number=part_number, url=url))


def initiate_upload(payload):
    key = f"uploads/{uuid.uuid4()}_{payload.filename}"
    content_type = payload.content_type

    # Start multipart upload
    response = s3.create_multipart_upload(
        Bucket=settings.S3_TEMP_BUCKET,
        Key=key,
        ContentType=content_type,
    )
    upload_id = response["UploadId"]

    # Generate presigned URLs for each chunk
    presigned_urls: List[PartPresignedURL] = []
    for part_num in range(1, payload.chunk_count + 1):
        url = s3.generate_presigned_url(
            ClientMethod="upload_part",
            Params={
                "Bucket": settings.S3_TEMP_BUCKET,
                "Key": key,
                "UploadId": upload_id,
                "PartNumber": part_num,
            },
            ExpiresIn=3600,
        )
        presigned_urls.append(PartPresignedURL(part_number=part_num, url=url))

    return {
        "key": key,
        "upload_id": upload_id,
        "presigned_urls": presigned_urls,
    }


def generate_presigned_url(filename: str):
    key = f"uploads/{uuid4()}_{filename}"
    bucket = settings.S3_TEMP_BUCKET
    if not bucket:
        raise ValueError("S3_TEMP_BUCKET is not set in the environment variables.")

    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=3600,
    )

    return {"presigned_url": url, "upload_path": key}
