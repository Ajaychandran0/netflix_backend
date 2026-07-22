import logging
import time
import redis

from .serializer import serialize_event


class StreamProducer:
    def __init__(self, redis_url: str):
        self.redis = redis.Redis.from_url(
            redis_url,
            decode_responses=True,
        )

    def publish(
        self,
        stream: str,
        event: dict,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        payload = serialize_event(event)

        for attempt in range(max_retries):
            try:
                self.redis.xadd(stream, payload)

                logging.info(
                    "Published event to %s: %s",
                    stream,
                    payload,
                )
                return

            except redis.exceptions.RedisError as e:
                logging.error(
                    "Redis publish failed (attempt %s): %s",
                    attempt + 1,
                    e,
                )
                time.sleep(retry_delay)

        raise RuntimeError("Failed to publish event to Redis stream after retries")