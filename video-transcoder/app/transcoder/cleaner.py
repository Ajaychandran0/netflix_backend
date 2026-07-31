"""
🧼 Future Enhancements

Move to a background deletion queue.
Keep deleted file in a “quarantine” bucket for X hours (if user reports an error).
Add a retry logic if S3 delete fails.

"""

from app.core.config import get_s3_client, static_config
from app.core.logger import logger


s3 = get_s3_client()


def cleanup(
    upload_path: str,
) -> None:
    """
    Perform cleanup after successful video processing.

    Current responsibilities:
    - Delete the original uploaded video from the temporary bucket.

    Args:
        upload_path:
            Object key of the original uploaded video inside the
            temporary upload bucket.
    """

    try:
        logger.info(
            "Deleting original upload: s3://%s/%s",
            static_config.s3_temp_bucket,
            upload_path,
        )

        s3.delete_object(
            Bucket=static_config.s3_temp_bucket,
            Key=upload_path,
        )

        logger.info(
            "Original upload deleted successfully."
        )

    except Exception:
        logger.exception(
            "Failed to delete original upload: %s",
            upload_path,
        )
        raise