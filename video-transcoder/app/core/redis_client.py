import redis.asyncio as redis
from app.core.config import static_config

redis_client = redis.from_url(static_config.redis_url, decode_responses=True)
