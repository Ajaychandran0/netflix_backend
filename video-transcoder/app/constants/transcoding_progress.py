"""
Configuration used for calculating overall transcoding progress.

The weights represent the expected CPU/time contribution
of each resolution variant.
"""


TRANSCODING_WEIGHTS = {
    "240p": 0.05,
    "360p": 0.10,
    "480p": 0.15,
    "720p": 0.25,
    "1080p": 0.45,
}


# Minimum percentage change required before publishing
# a new progress update.
PROGRESS_CHANGE_THRESHOLD = 2.0


# Minimum time between Redis progress updates.
# Prevents excessive writes during FFmpeg processing.
PROGRESS_UPDATE_INTERVAL_SECONDS = 5