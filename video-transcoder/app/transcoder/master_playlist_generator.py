from pathlib import Path

from app.constants.asset_names import MASTER_PLAYLIST_FILENAME
from app.constants.transcoding_presets import TRANSCODING_PRESETS

from app.core.logger import logger


def generate_master_playlist(
    output_map: dict[str, Path],
    output_dir: Path,
) -> Path:
    """
    Generate the HLS master playlist.

    Responsibilities:
    - Validate generated rendition playlists.
    - Generate a standards-compliant master.m3u8.
    - Return the local master playlist path.

    """

    if not output_map:
        raise ValueError(
            "No transcoded variants were generated."
        )
        
    if not output_dir.exists():
        raise FileNotFoundError(
            f"Output directory does not exist: {output_dir}"
        )

    # --------------------------------------------------
    # Validate generated playlists
    # --------------------------------------------------

    for resolution, playlist in output_map.items():

        if resolution not in TRANSCODING_PRESETS:
            raise ValueError(
                f"Unsupported resolution '{resolution}'."
            )

        if not playlist.exists():
            raise FileNotFoundError(
                f"Playlist not found: {playlist}"
            )

    master_playlist_path = (
        output_dir
        / MASTER_PLAYLIST_FILENAME
    )

    lines = [
        "#EXTM3U",
        "#EXT-X-VERSION:3",
    ]

    # --------------------------------------------------
    # Lowest quality -> Highest quality
    # --------------------------------------------------

    sorted_variants = sorted(
        output_map.items(),
        key=lambda item: TRANSCODING_PRESETS[
            item[0]
        ].bandwidth,
    )

    for resolution, playlist_path in sorted_variants:

        preset = TRANSCODING_PRESETS[
            resolution
        ]

        relative_playlist = (
            playlist_path.relative_to(output_dir)
        )

        lines.append(
            (
                "#EXT-X-STREAM-INF:"
                f"BANDWIDTH={preset.bandwidth},"
                f"RESOLUTION={preset.scale}"
            )
        )

        lines.append(
            str(relative_playlist)
        )

    master_playlist_path.write_text(
        "\n".join(lines)
    )

    logger.info(
        "Generated master playlist: %s",
        master_playlist_path,
    )

    return master_playlist_path