"""
🧼 Future Enhancements

Move to a background deletion queue.
Keep deleted file in a “quarantine” bucket for X hours (if user reports an error).
Add a retry logic if S3 delete fails.
"""

import boto3
from app.core.config import settings
from app.core.logger import logger

s3 = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint_url,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region,
)


def delete_temp_upload(file_key: str):
    """
    Deletes the original uploaded video from the uploads location in S3/MinIO.

    Args:
        file_key (str): Path relative to bucket (e.g., "uploads/test.mp4")
    """
    try:
        s3.delete_object(Bucket=settings.s3_temp_bucket, Key=file_key)
        logger.info(
            f"Deleted original uploaded file: s3://{settings.s3_temp_bucket}/{file_key}"
        )
    except Exception as e:
        logger.error(f"Failed to delete original upload: {file_key} - {e}")
        # Don't raise, since upload already succeeded
