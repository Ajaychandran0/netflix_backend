from pathlib import Path
import asyncio

from app.core.logger import logger
from app.schemas.video import VideoMetadata
from app.schemas.transcoding import TranscodingPreset
from app.constants.transcoding import TRANSCODING_PRESETS


async def transcode_video_to_hls(
    input_path: Path,
    output_base_dir: Path,
    resolutions: list[str],
    video_metadata: VideoMetadata,
    progress_callback=None,
) -> dict[str, Path]:
    """
    Transcode a source video into multiple HLS variants.

    Responsibilities
    ----------------
    - Generate HLS outputs.
    - Report per-resolution transcoding progress.
    - Return generated playlist paths.

    This function does NOT:
    - Update Redis
    - Publish events
    - Update database

    Args:
        input_path:
            Local source video.

        output_base_dir:
            Directory where HLS outputs will be generated.

        resolutions:
            Requested output resolutions.

        video_metadata:
            Metadata extracted from the original source video.

        progress_callback:
            Optional async callback.

            Signature:

                async callback(
                    resolution: str,
                    percentage: float,
                )

    Returns:
        Mapping of resolution -> generated playlist path.
    """

    # --------------------------------------------------
    # Validate inputs
    # --------------------------------------------------
    if not input_path.exists():
        raise FileNotFoundError(
            f"Input video not found: {input_path}"
        )

    if video_metadata.duration_ms <= 0:
        raise ValueError("Video duration must be greater than zero to track transcoding progress.")

    invalid_resolutions = (
        set(resolutions) - set( TRANSCODING_PRESETS.keys())
    )

    if invalid_resolutions:
        raise ValueError(
            f"Unsupported resolutions: {invalid_resolutions}"
        )

    output_base_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_map: dict[str, Path] = {}

    async def _transcode_variant(
        preset: TranscodingPreset,
    ):
        """
        Transcode a single HLS resolution variant.
        """

        resolution = preset.resolution
        output_dir = output_base_dir / resolution

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        playlist_path = output_dir / "index.m3u8"

        segment_pattern = (
            output_dir / "segment_%03d.ts"
        )

        command = [
            "ffmpeg",

            "-i",
            str(input_path),

            # Scale
            "-vf",
            f"scale={preset.scale}",

            # Audio
            "-c:a",
            "aac",

            "-ar",
            "48000",

            # Video
            "-c:v",
            "h264",

            "-profile:v",
            "main",

            "-crf",
            "20",

            "-sc_threshold",
            "0",

            "-g",
            "48",

            "-keyint_min",
            "48",

            # HLS
            "-hls_time",
            "4",

            "-hls_playlist_type",
            "vod",

            "-b:v",
            preset.bitrate,

            "-maxrate",
            preset.maxrate,

            "-bufsize",
            preset.bufsize,

            "-hls_segment_filename",
            str(segment_pattern),

            # Machine-readable progress
            "-progress",
            "pipe:1",

            # Less noisy stdout
            "-nostats",

            str(playlist_path),
        ]

        logger.info(
            "[%s] Starting transcoding",
            resolution,
        )

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        async def _read_progress():
            """
            Read FFmpeg machine-readable progress.

            Example:

                out_time_us=5000000
                progress=continue
            """

            output_time_us = None

            async def publish_progress() -> None:
                if output_time_us is None or not progress_callback:
                    return

                processed_ms = output_time_us / 1000
                raw_percent = processed_ms / video_metadata.duration_ms * 100
                # FFmpeg can report the full media duration before it has
                # finished muxing and closing the HLS playlist. Reserve 100%
                # for the successful process exit and playlist check below.
                percentage = max(0.0, min(raw_percent, 99.0))
                await progress_callback(resolution, round(percentage, 2))

            while True:
                line = await process.stdout.readline()
                if not line:
                    break

                decoded = line.decode().strip()
                if "=" not in decoded:
                    continue

                key, value = decoded.split("=", 1)

                if key in {"out_time_us", "out_time_ms"}:
                    # FFmpeg's legacy out_time_ms field is also in
                    # microseconds, despite its name. Prefer the correctly
                    # named out_time_us value when both are present.
                    try:
                        parsed_time_us = int(value)
                    except ValueError:
                        continue
                    if parsed_time_us >= 0 and (key == "out_time_us" or output_time_us is None):
                        output_time_us = parsed_time_us
                elif key == "out_time" and output_time_us is None:
                    try:
                        hours, minutes, seconds = value.split(":")
                        output_time_us = int(
                            (int(hours) * 3600 + int(minutes) * 60 + float(seconds)) * 1_000_000
                        )
                    except ValueError:
                        continue
                elif key == "progress":
                    await publish_progress()
                    output_time_us = None

            # Process a final partial block if FFmpeg closed stdout before its
            # terminating progress marker.
            await publish_progress()

        async def _read_stderr():
            """
            Drain stderr so FFmpeg
            never blocks because
            of a full buffer.

            We only log stderr if
            transcoding fails.
            """

            stderr_lines = []

            while True:

                line = await process.stderr.readline()

                if not line:
                    break

                stderr_lines.append(
                    line.decode()
                )

            return "".join(stderr_lines)

        progress_task = asyncio.create_task(
            _read_progress()
        )

        stderr_task = asyncio.create_task(
            _read_stderr()
        )

        try:

            await process.wait()

            await progress_task

            stderr_output = await stderr_task

        except asyncio.CancelledError:

            process.kill()

            raise

        if process.returncode != 0:

            logger.error(
                "[%s] FFmpeg failed:\n%s",
                resolution,
                stderr_output,
            )

            raise RuntimeError(
                f"FFmpeg failed for {resolution}"
            )

        if not playlist_path.exists():

            raise RuntimeError(
                f"HLS playlist not generated: {playlist_path}"
            )

        output_map[resolution] = playlist_path

        # Ensure final progress is emitted.
        if progress_callback:

            await progress_callback(
                resolution,
                100.0,
            )

        logger.info(
            "[%s] Completed",
            resolution,
        )

    # --------------------------------------------------
    # Launch all requested variants
    # --------------------------------------------------
    tasks = [
        _transcode_variant(
            preset=TRANSCODING_PRESETS[resolution],
        )
        for resolution in resolutions
    ]

    await asyncio.gather(*tasks)

    logger.info(
        "Successfully generated %d HLS variants",
        len(output_map),
    )

    return output_map
