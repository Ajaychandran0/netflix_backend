import os
from app.core.logger import logger

RESOLUTION_META = {
    "240p":  {"bandwidth": 400_000,  "resolution": "426x240"},
    "360p":  {"bandwidth": 800_000,  "resolution": "640x360"},
    "480p":  {"bandwidth": 1_200_000, "resolution": "854x480"},
    "720p":  {"bandwidth": 2_500_000, "resolution": "1280x720"},
    "1080p": {"bandwidth": 5_000_000, "resolution": "1920x1080"},
}


def generate_master_playlist(output_map: dict, output_dir: str) -> str:
    """
    Generate HLS master.m3u8 from transcoder output_map
    """

    master_path = os.path.join(output_dir, "master.m3u8")

    lines = [
        "#EXTM3U",
        "#EXT-X-VERSION:3"
    ]

    # sort by quality (low → high)
    sorted_res = sorted(
        output_map.keys(),
        key=lambda r: RESOLUTION_META[r]["bandwidth"]
    )

    for res in sorted_res:
        meta = RESOLUTION_META.get(res)
        if not meta:
            continue

        playlist_path = f"{res}/master.m3u8"

        lines.append(
            f"#EXT-X-STREAM-INF:BANDWIDTH={meta['bandwidth']},RESOLUTION={meta['resolution']}"
        )
        lines.append(playlist_path)

    content = "\n".join(lines)

    os.makedirs(output_dir, exist_ok=True)

    with open(master_path, "w") as f:
        f.write(content)

    logger.info(f"Master playlist generated at {master_path}")

    return master_path