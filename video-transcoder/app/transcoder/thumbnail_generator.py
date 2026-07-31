from pathlib import Path
import subprocess

from app.constants.video_processing import THUMBNAIL_CAPTURE_PERCENTAGE
from app.constants.asset_names import (
    THUMBNAIL_FILENAME,
    TRANSCODER_OUTPUT_DIR,
)
from app.core.logger import logger


def generate_thumbnail(
    input_path: Path,
    duration_ms: int,
) -> Path:
    """
    Generate a thumbnail for a video.

    The thumbnail is captured at approximately 20% of the video's duration
    (instead of a fixed timestamp) to reduce the chance of selecting an
    intro screen or black frame.

    The generated thumbnail is always written to:

        TRANSCODER_OUTPUT_DIR / THUMBNAIL_FILENAME

    Args:
        input_path:
            Local source video.

        duration_ms:
            Total duration of the source video.

    Returns:
        Path to the generated thumbnail.

    Raises:
        RuntimeError:
            If FFmpeg fails.

        FileNotFoundError:
            If the thumbnail was not created.
    """

    output_path = (
        TRANSCODER_OUTPUT_DIR
        / THUMBNAIL_FILENAME
    )

    # Capture a frame around 20% into the video.
    # Avoid requesting frame at 0 seconds.
    timestamp = max(
        1,
        int((duration_ms / 1000) * THUMBNAIL_CAPTURE_PERCENTAGE),
    )

    command = [
        "ffmpeg",

        "-ss",
        str(timestamp),

        "-i",
        str(input_path),

        "-frames:v",
        "1",

        "-q:v",
        "2",

        "-an",
        "-sn",
        "-dn",

        "-y",

        str(output_path),
    ]

    logger.info(
        "Generating thumbnail at %ss",
        timestamp,
    )

    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    except subprocess.CalledProcessError as exc:
        logger.error(
            "Thumbnail generation failed: %s",
            exc.stderr,
        )
        raise RuntimeError(
            "Failed to generate thumbnail."
        ) from exc

    if not output_path.exists():
        raise FileNotFoundError(
            f"Thumbnail not generated: {output_path}"
        )

    logger.info(
        "Thumbnail generated: %s",
        output_path,
    )

    return output_path