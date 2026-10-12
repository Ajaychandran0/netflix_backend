class RedisKeys:
    @staticmethod
    def video_progress(video_id: str, attempt_id: str) -> str:
        # Attempt-scoped keys keep late updates from an older worker isolated.
        return f"video:progress:{video_id}:{attempt_id}"
