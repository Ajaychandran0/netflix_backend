from pathlib import Path 
from botocore.exceptions import BotoCoreError, ClientError
from app.core.config import static_config, get_s3_client
from app.core.logger import logger


def download_video_from_s3(object_key: str, local_filename: str = None) -> str:
    """
    Download a video from S3/MinIO bucket and save it to a local file.

    Args:
        object_key (str): The S3 object key (e.g., "uploads/video.mp4").
        local_filename (str, optional): If not provided, it will be derived from object_key.

    Returns:
        str: Path to the local downloaded file.
    """
    
    s3 = get_s3_client()

    if not local_filename:
        filename = Path(object_key).name
        local_path = static_config.temp_dir / filename
    else:
        local_path = Path(local_filename)

    try:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Downloading {object_key} from bucket {static_config.s3_temp_bucket} to {local_path}")
        
        s3.download_file(static_config.s3_temp_bucket, object_key, str(local_path))
        
        logger.info(f"Download completed: {local_path}")
        return str(local_path)
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to download {object_key} from S3: {e}")
        raise
