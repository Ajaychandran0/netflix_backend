import os
from typing import List

def generate_master_playlist(
    resolutions: List[str],
    video_id: str,
    base_url: str,
    output_dir: str,
):
    """
    Create master index.m3u8 pointing to variant playlists for different resolutions.

    :param resolutions: list of resolution names like ["240p", "360p", "480p"]
    :param video_id: unique video identifier
    :param base_url: base URL or relative path for the HLS segments
    :param output_dir: local folder where the final index.m3u8 will be saved
    """
    variant_lines = [
        "#EXTM3U",
        "#EXT-X-VERSION:3"
    ]

    resolution_to_bandwidth = {
        "240p": 400_000,
        "360p": 800_000,
        "480p": 1_200_000,
        "720p": 2_000_000,
        "1080p": 3_000_000,
    }

    for res in resolutions:
        bw = resolution_to_bandwidth.get(res, 1_000_000)
        stream_url = f"{base_url}/{res}/master.m3u8"
        variant_lines.append(f"#EXT-X-STREAM-INF:BANDWIDTH={bw},RESOLUTION={res.replace('p', '')}x{get_height(res)}")
        variant_lines.append(stream_url)

    playlist_path = os.path.join(output_dir, "index.m3u8")
    with open(playlist_path, "w") as f:
        f.write("\n".join(variant_lines))

    return playlist_path


def get_height(res: str) -> int:
    """Return height based on resolution string."""
    return {
        "240p": 240,
        "360p": 360,
        "480p": 480,
        "720p": 720,
        "1080p": 1080,
    }.get(res, 360)
 