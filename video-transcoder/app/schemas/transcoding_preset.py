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