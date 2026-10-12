from pathlib import Path

from app.core.s3_client import get_s3_client
from app.core.config import static_config
from app.core.logger import logger

from app.schemas.assets import UploadedAssets
from app.constants.assets import THUMBNAIL_FILENAME

s3 = get_s3_client()


def upload_transcoded_outputs(
    *,
    video_id: str,
    output_dir: Path,
    local_master_playlist_path: Path,
    local_thumbnail_path: Path,
) -> UploadedAssets:
    """
    Upload transcoded video assets and thumbnail.
    Video/HLS assets are uploaded to the private video bucket.
    Thumbnail is uploaded separately to the public thumbnail bucket.
    
    Returns
    -------
    UploadedAssets
        Object keys of important generated assets.
    """

    # --------------------------------------------------
    # Upload video/HLS assets
    # --------------------------------------------------

    master_playlist_object_key: str | None = None
    thumbnail_object_key: str | None = None

    for local_file in output_dir.rglob("*"):

        if not local_file.is_file():
            continue
        
        # Thumbnail is uploaded separately.
        if local_file == local_thumbnail_path:
            continue


        relative_path = local_file.relative_to(output_dir)

        object_key = (
            Path(video_id) / relative_path
        ).as_posix()

        logger.info(
            "Uploading %s -> %s",
            local_file,
            object_key,
        )

        s3.upload_file(
            Filename=str(local_file),
            Bucket=static_config.s3_video_bucket,
            Key=object_key,
        )

        if local_file == local_master_playlist_path:
            master_playlist_object_key = object_key


    if master_playlist_object_key is None:
        raise RuntimeError(
            "Master playlist was not uploaded."
        )
        
    # --------------------------------------------------
    # Upload thumbnail
    # --------------------------------------------------

    thumbnail_object_key = (
        Path(video_id) / THUMBNAIL_FILENAME
    ).as_posix()


    logger.info(
        "Uploading thumbnail %s -> %s",
        local_thumbnail_path,
        thumbnail_object_key,
    )

    s3.upload_file(
        Filename=str(local_thumbnail_path),
        Bucket=static_config.s3_thumbnail_bucket,
        Key=thumbnail_object_key,
    )

    logger.info(
        "Uploaded transcoded assets successfully."
    )

    return UploadedAssets(
        master_playlist_object_key=master_playlist_object_key,
        thumbnail_object_key=thumbnail_object_key,
    )