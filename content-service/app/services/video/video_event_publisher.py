from app.services.queue.redis_stream_producer import RedisStreamProducer

class VideoProcessingEventPublisher:
    def __init__(self):
        self.stream_name = "video:processing:stream"
        self.producer = RedisStreamProducer()

    def enqueue_video(self, event: dict) -> None:
        self.producer.publish(self.stream_name, event)
        
