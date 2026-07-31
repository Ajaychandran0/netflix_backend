from pathlib import Path 
from botocore.exceptions import BotoCoreError, ClientError
from app.core.logger import logger

from app.core.config import static_config, get_s3_client
from app.constants.assets import SOURCE_VIDEO_DIR

def download_source_video(
    object_key: str,
    local_path: str| Path | None = None
) -> Path:
    """
    Download a video from S3/MinIO bucket and save it to a local file.

    Args:
        object_key (str): The S3 object key (e.g., "uploads/video.mp4").
        local_path (str | Path | None, optional): If not provided, it will be derived from object_key.

    Returns:
        Path: Path to the local downloaded file.
    """
    
    s3 = get_s3_client()

    if not local_path:
        filename = Path(object_key).name
        local_path = SOURCE_VIDEO_DIR / filename
    else:
        local_path = Path(local_path)

    try:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            "Downloading %s from bucket %s to %s",
            object_key,
            static_config.s3_temp_bucket,
            local_path,
        )        
        s3.download_file(static_config.s3_temp_bucket, object_key, str(local_path))
        
        logger.info(
            "Download completed: %s",
            local_path,
        )
        
        return local_path
    
    except (BotoCoreError, ClientError):
        logger.exception(
            "Failed to download object %s from S3",
            object_key,
        )
        raise
