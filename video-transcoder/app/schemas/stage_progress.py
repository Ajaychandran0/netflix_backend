from pydantic import BaseModel, ConfigDict


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