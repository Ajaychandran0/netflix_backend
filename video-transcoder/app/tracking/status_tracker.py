from datetime import datetime, timezone
from uuid import UUID

from app.constants.processing import ProcessingStage, ProcessingStatus
from app.constants.redis import RedisKeys
from app.core.redis_client import redis_client


class StatusTracker:
    DEFAULT_TTL_SECONDS = 3600          # 1 hour
    COMPLETED_TTL_SECONDS = 600         # 10 minutes

    def __init__(self, video_id: UUID, attempt_id: str):
        self.video_id = str(video_id)
        self.attempt_id = str(attempt_id)
        self.key = RedisKeys.video_progress(self.video_id, self.attempt_id)

    async def start(self) -> None:
        """
        Initializes the processing status.
        """
        await self._save(
            progress=0,
            stage=ProcessingStage.DOWNLOADING,
            status=ProcessingStatus.PROCESSING,
        )

    async def update_stage(
        self,
        stage: ProcessingStage,
    ) -> None:
        """
        Updates only the processing stage.
        """
        await self._save(stage=stage)

    async def update_progress(
        self,
        progress: int | float,
    ) -> None:
        """
        Updates only the progress percentage.
        """
        progress = max(0, min(progress, 100))
        # Progress callbacks from parallel FFmpeg workers can arrive out of
        # order. Compare and update atomically so a late callback cannot lower
        # the visible value.
        await redis_client.eval(
            """
            local current = tonumber(redis.call('HGET', KEYS[1], 'progress') or '0')
            local incoming = tonumber(ARGV[1])
            if incoming > current then
                redis.call('HSET', KEYS[1], 'progress', incoming)
            end
            redis.call('HSET', KEYS[1], 'updated_at', ARGV[2])
            redis.call('EXPIRE', KEYS[1], ARGV[3])
            return math.max(current, incoming)
            """,
            1,
            self.key,
            progress,
            datetime.now(timezone.utc).isoformat(),
            self.DEFAULT_TTL_SECONDS,
        )

    async def complete(self) -> None:
        """
        Marks processing as completed.
        """
        await self._save(
            progress=100,
            stage=ProcessingStage.CLEANUP,
            status=ProcessingStatus.COMPLETED,
        )

        await redis_client.expire(
            self.key,
            self.COMPLETED_TTL_SECONDS,
        )

    async def fail(
        self,
        stage: ProcessingStage,
    ) -> None:
        """
        Marks processing as failed.
        """
        await self._save(
            stage=stage,
            status=ProcessingStatus.FAILED,
        )

        await redis_client.expire(
            self.key,
            self.COMPLETED_TTL_SECONDS,
        )

    async def clear(self) -> None:
        """
        Removes the progress key immediately.
        """
        await redis_client.delete(self.key)

    async def _save(
        self,
        *,
        progress: int | None = None,
        stage: ProcessingStage | None = None,
        status: ProcessingStatus | None = None,
    ) -> None:
        """
        Saves only the supplied fields.
        """

        payload = {}

        if progress is not None:
            payload["progress"] = progress

        if stage is not None:
            payload["stage"] = stage.value

        if status is not None:
            payload["status"] = status.value

        payload["updated_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        await redis_client.hset(
            self.key,
            mapping=payload,
        )

        await redis_client.expire(
            self.key,
            self.DEFAULT_TTL_SECONDS,
        )
