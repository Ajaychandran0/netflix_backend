import os
import subprocess
from app.core.logger import logger


def generate_thumbnail(input_path: str, output_path: str, timestamp: int = 5) -> str:
    """
    Generate a thumbnail from the video using FFmpeg.
    
    :param input_path: Path to the source video file
    :param output_path: Path where the thumbnail.jpg will be saved
    :param timestamp: Timestamp (in seconds) from where to capture the thumbnail
    :return: Path to the generated thumbnail
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        command = [
            "ffmpeg",
            "-ss", str(timestamp),
            "-i", input_path,
            "-frames:v", "1",
            "-q:v", "2",  # high quality thumbnail
            "-an",
            "-sn",
            "-dn",
            "-y",  # overwrite
            output_path
        ]

        logger.info(f"Generating thumbnail: {' '.join(command)}")
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Thumbnail saved at {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg thumbnail failed: {e.stderr}")
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error generating thumbnail: {e}")
        raise
