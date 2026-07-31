import json
import mimetypes
import subprocess
from pathlib import Path

from app.core.logger import logger
from app.schemas.video import VideoMetadata


def extract_video_metadata(video_path: Path) -> VideoMetadata:
    """
    Extract metadata from the original source video using ffprobe.

    Args:
        video_path: Local path to the source video.

    Returns:
        VideoMetadata containing source video information.

    Raises:
        FileNotFoundError: If the video file does not exist.
        RuntimeError: If ffprobe fails.
        ValueError: If required metadata cannot be extracted.
    """

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    logger.info("Extracting metadata from %s", video_path)

    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

    except subprocess.CalledProcessError as exc:
        logger.exception("ffprobe failed for %s", video_path)
        raise RuntimeError("Failed to extract video metadata.") from exc

    metadata = json.loads(result.stdout)

    video_stream = next(
        (
            stream
            for stream in metadata.get("streams", [])
            if stream.get("codec_type") == "video"
        ),
        None,
    )

    if video_stream is None:
        raise ValueError("No video stream found.")
    
    width = video_stream.get("width")
    height = video_stream.get("height")
    
    if width is None or height is None:
        raise ValueError("Unable to determine source video resolution.")

    duration = metadata.get("format", {}).get("duration")

    if duration is None:
        raise ValueError("Unable to determine video duration.")

    mime_type, _ = mimetypes.guess_type(video_path.name)

    video_metadata = VideoMetadata(
        duration_ms=int(float(duration) * 1000),
        source_width=width,
        source_height=height,
        source_file_size_bytes=video_path.stat().st_size,
        mime_type=mime_type or "application/octet-stream",
    )

    logger.info(
        "Metadata extracted successfully for %s",
        video_path,
    )

    return video_metadata