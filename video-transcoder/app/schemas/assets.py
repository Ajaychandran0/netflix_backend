'''
    Later Generated assets Schema, Published assets schemas etc.. can be added here.
'''

from pydantic import BaseModel


class UploadedAssets(BaseModel):
    """
    Object keys of uploaded transcoded assets.

    These keys are persisted in the database and used by
    downstream services.
    """

    master_playlist_object_key: str
    thumbnail_object_key: str