from app.core.config.env import settings
from platform_messaging import StreamProducer

class VideoProcessingEventPublisher:
    def __init__(self):
        self.stream_name = settings.VIDEO_PROCESSING_STREAM
        self.producer = StreamProducer(settings.REDIS_URL)


    def enqueue_video(self, event: dict) -> None:
        self.producer.publish(self.stream_name, event)
        
