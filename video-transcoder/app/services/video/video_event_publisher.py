from app.core.config import static_config
from platform_messaging import StreamProducer

class VideoEventsPublisher:
    def __init__(self):
        self.stream_name = static_config.video_events_stream
        self.producer = StreamProducer(static_config.redis_url)


    def enqueue_video(self, event: dict) -> None:
        self.producer.publish(self.stream_name, event)
        
