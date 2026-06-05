from app.services.queue.redis_stream_producer import RedisStreamProducer
from app.core.config.env import settings

class VideoProcessingEventPublisher:
    def __init__(self):
        self.stream_name = settings.REDIS_STREAM_NAME
        self.producer = RedisStreamProducer()

    def enqueue_video(self, event: dict) -> None:
        self.producer.publish(self.stream_name, event)
        
