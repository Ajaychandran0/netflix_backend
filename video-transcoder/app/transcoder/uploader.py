from pathlib import Path

from app.core.config import get_s3_client, static_config
from app.core.logger import logger

from app.schemas.uploaded_assets import UploadedAssets

s3 = get_s3_client()


def upload_transcoded_outputs(
    *,
    video_id: str,
    output_dir: Path,
    local_master_playlist_path: Path,
    local_thumbnail_path: Path,
) -> UploadedAssets:
    """
    Upload every transcoded asset produced by the transcoder.

    All files inside ``output_dir`` are uploaded recursively to

        <s3_transcoded_base_path>/<video_id>/

    While uploading, this function captures the S3 object keys of the
    generated master playlist and thumbnail so callers can persist them.

    Returns
    -------
    UploadedAssets
        Object keys of important generated assets.
    """

    s3_prefix = (
        Path(static_config.s3_transcoded_base_path)
        / video_id
    )

    master_playlist_object_key: str | None = None
    thumbnail_object_key: str | None = None

    for local_file in output_dir.rglob("*"):

        if not local_file.is_file():
            continue

        relative_path = local_file.relative_to(output_dir)

        object_key = (
            s3_prefix / relative_path
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

        elif local_file == local_thumbnail_path:
            thumbnail_object_key = object_key

    if master_playlist_object_key is None:
        raise RuntimeError(
            "Master playlist was not uploaded."
        )

    if thumbnail_object_key is None:
        raise RuntimeError(
            "Thumbnail was not uploaded."
        )

    logger.info(
        "Uploaded transcoded assets successfully."
    )

    return UploadedAssets(
        master_playlist_object_key=master_playlist_object_key,
        thumbnail_object_key=thumbnail_object_key,
    )