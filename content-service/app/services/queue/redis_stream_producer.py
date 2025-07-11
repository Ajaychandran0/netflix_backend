import json
import redis
import time
import logging

from app.services.queue.base import BaseQueueProducer
from app.core.config.env import settings 

class RedisStreamProducer(BaseQueueProducer):
    def __init__(self):
        self.redis = redis.Redis.from_url(settings.REDIS_URL)
        
    def sanitize_event_data(self, data: dict) -> dict:
        return {
            k: v
            for k, v in data.items()
            if v is not None
        }


    def publish(self, stream_name: str, data: dict, max_retries: int = 3, retry_delay: float = 1.0) -> None:
        sanitized_data = self.sanitize_event_data(data)
        for attempt in range(max_retries):
            try:
                self.redis.xadd(stream_name, {k: json.dumps(v) for k, v in sanitized_data.items()})
                return
            except redis.exceptions.RedisError as e:
                logging.error(f"Redis stream error (attempt {attempt + 1}): {e}")
                time.sleep(retry_delay)
        # All retries failed
        raise RuntimeError("Failed to enqueue message to Redis stream after retries")
