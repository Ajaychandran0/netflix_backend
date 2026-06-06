import os
import asyncio
from typing import List
from app.core.logger import logger

FFMPEG_PRESETS = {
    "240p": "426x240",
    "360p": "640x360",
    "480p": "854x480",
    "720p": "1280x720",
    "1080p": "1920x1080",
}

async def transcode_video_to_hls(input_path: str, output_base_dir: str, resolutions: List[str]) -> dict:
    """
    Transcode video to multiple HLS resolutions in parallel.

    Args:
        input_path (str): Path to the downloaded input video.
        output_base_dir (str): Base dir to save transcoded outputs (e.g. /tmp/hls_outputs/<video_id>)
        resolutions (List[str]): e.g., ["240p", "360p", "480p"]

    Returns:
        dict: Mapping of resolution -> HLS .m3u8 output path
    """
    os.makedirs(output_base_dir, exist_ok=True)
    output_map = {}

    async def _transcode(resolution: str, size: str):
        output_dir = os.path.join(output_base_dir, resolution)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "index.m3u8")
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vf", f"scale={size}",
            "-c:a", "aac",
            "-ar", "48000",
            "-c:v", "h264",
            "-profile:v", "main",
            "-crf", "20",
            "-sc_threshold", "0",
            "-g", "48",
            "-keyint_min", "48",
            "-hls_time", "4",
            "-hls_playlist_type", "vod",
            "-b:v", "1400k",
            "-maxrate", "1498k",
            "-bufsize", "2100k",
            "-hls_segment_filename", os.path.join(output_dir, "segment_%03d.ts"),
            output_path
        ]

        logger.info(f"[{resolution}] Starting transcoding to {output_path}")
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            logger.error(f"[{resolution}] Transcoding failed: {stderr.decode()}")
            raise RuntimeError(f"FFmpeg failed for {resolution}")

        logger.info(f"[{resolution}] Transcoding completed: {output_path}")
        output_map[resolution] = output_path

    tasks = [
        _transcode(res, size)
        for res, size in FFMPEG_PRESETS.items()
        if res in resolutions
    ]
    
    await asyncio.gather(*tasks)
    return output_map
