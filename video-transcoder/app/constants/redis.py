class RedisKeys:
    @staticmethod
    def video_progress(video_id: str) -> str:
        return f"video:progress:{video_id}"