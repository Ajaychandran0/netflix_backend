from contextlib import asynccontextmanager
from redis.asyncio import Redis
from datetime import datetime


class StatusTracker:
    def __init__(self, redis: Redis):
        self.redis = redis

    def _status_key(self, video_id: str) -> str:
        return f"video:status:{video_id}"

    async def update_status(
        self,
        video_id: str,
        stage: str,
        current_task: str = "",
        progress: str = "",
        error: str = "",
    ):
        key = self._status_key(video_id)
        now = datetime.utcnow().isoformat()

        update_data = {
            "stage": stage,
            "current_task": current_task,
            "progress": progress,
            "updated_at": now,
        }

        if error:
            update_data["error"] = error

        await self.redis.hset(key, mapping=update_data)

    async def mark_failed(self, video_id: str, error: str):
        await self.update_status(video_id, stage="failed", error=error)

    async def mark_completed(self, video_id: str):
        await self.update_status(
            video_id, stage="completed", progress="100%", current_task="done"
        )

    @asynccontextmanager
    async def track_stage(
        self, video_id: str, stage: str, task: str, progress: str = ""
    ):
        """Context manager to automatically update status before and after a task"""
        await self.update_status(
            video_id, stage=stage, current_task=task, progress=progress
        )
        try:
            yield
        except Exception as e:
            await self.mark_failed(video_id, error=str(e))
            raise
