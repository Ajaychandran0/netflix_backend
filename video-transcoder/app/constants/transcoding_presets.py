from app.schemas.transcoding_preset import TranscodingPreset


TRANSCODING_PRESETS: dict[str, TranscodingPreset] = {
    "240p": TranscodingPreset(
        resolution="240p",
        scale="426x240",
        bitrate="400k",
        maxrate="428k",
        bufsize="600k",
        bandwidth=400_000,
    ),

    "360p": TranscodingPreset(
        resolution="360p",
        scale="640x360",
        bitrate="800k",
        maxrate="856k",
        bufsize="1200k",
        bandwidth=800_000,
    ),

    "480p": TranscodingPreset(
        resolution="480p",
        scale="854x480",
        bitrate="1400k",
        maxrate="1498k",
        bufsize="2100k",
        bandwidth=1_200_000,
    ),

    "720p": TranscodingPreset(
        resolution="720p",
        scale="1280x720",
        bitrate="2800k",
        maxrate="2996k",
        bufsize="4200k",
        bandwidth=2_500_000,

    ),

    "1080p": TranscodingPreset(
        resolution="1080p",
        scale="1920x1080",
        bitrate="5000k",
        maxrate="5350k",
        bufsize="7500k",
        bandwidth=5_000_000,
    ),
}

TRANSCODING_RESOLUTIONS = tuple(TRANSCODING_PRESETS)