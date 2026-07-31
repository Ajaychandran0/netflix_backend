from pydantic import BaseModel, ConfigDict


class TranscodingPreset(BaseModel):
    """
    Encoding configuration for a single HLS variant.
    """
    model_config = ConfigDict(frozen=True)
    resolution: str
    scale: str
    bitrate: str
    maxrate: str
    bufsize: str
    bandwidth: int
    


class StageProgressRange(BaseModel):
    """
    Represents the percentage range occupied by
    a processing stage within the overall pipeline.

    Example:

        TRANSCODING

        start = 10
        end = 85
    """

    model_config = ConfigDict(frozen=True)
    start: float
    end: float