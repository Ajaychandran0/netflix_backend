import os
from app.core.config import static_config, get_s3_client
from app.core.logger import logger

s3 = get_s3_client()

def upload_directory(local_dir: str, s3_base_path: str):
    """
    Recursively upload a local directory to S3/MinIO.
    """

    for root, _, files in os.walk(local_dir):

        for file in files:
            local_path = os.path.join(root, file)

            # Relative path from base dir
            rel_path = os.path.relpath(local_path, local_dir)

            # Final S3 object key
            s3_key = os.path.join(s3_base_path, rel_path).replace("\\", "/")

            try:
                s3.upload_file(
                    local_path,
                    static_config.s3_video_bucket,
                    s3_key
                )

                logger.info(
                    f"Uploaded {local_path} "
                    f"to s3://{static_config.s3_video_bucket}/{s3_key}"
                )

            except Exception as e:
                logger.error(f"Failed to upload {local_path}: {e}")
                raise


def upload_transcoded_outputs(
    video_id: str,
    local_output_dir: str,
):
    """
    Upload all transcoded outputs for a video.

    Example:
    local_output_dir:
        /tmp/video-transcoder/<video_id>/

    Uploads to:
        transcoded_videos/<video_id>/
    """

    s3_base_path = (
        f"{static_config.s3_transcoded_base_path}/{video_id}"
    )

    upload_directory(local_output_dir, s3_base_path)