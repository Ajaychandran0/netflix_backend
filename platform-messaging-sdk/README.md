# Platform Messaging SDK

A lightweight Python SDK for publishing and consuming Redis Stream events across the platform services.

## Overview

This package provides shared messaging primitives for microservices that need to:

- publish structured events to Redis Streams
- consume events from a consumer group
- serialize Python objects into Redis-safe string payloads
- retry failed processing with exponential backoff
- move permanently failed messages to a Dead Letter Queue (DLQ)

## Features

- `StreamProducer` for publishing events to Redis Streams
- `StreamConsumer` for consuming messages from a consumer group
- `serialize_event()` to convert Python values such as `dict`, `list`, `datetime`, `UUID`, `Decimal`, and `Enum` into Redis-friendly strings
- built-in retry and DLQ handling for message processing failures

## Package Structure

- `platform_messaging/producer.py` — event publishing client
- `platform_messaging/consumer.py` — stream consumer and retry logic
- `platform_messaging/serializer.py` — payload normalization for Redis writes
- `platform_messaging/__init__.py` — public exports

## Installation

This package is intended to be used as a local Python package in the monorepo.

Example:

```bash
pip install -e .
```

Or, if using Poetry:

```bash
poetry install
```

## Usage

### Publishing an event

```python
from platform_messaging import StreamProducer

producer = StreamProducer(redis_url="redis://localhost:6379/0")

producer.publish(
    stream="video-events",
    event={
        "event_type": "video.uploaded",
        "video_id": "123",
        "metadata": {"status": "completed"},
    },
)
```

### Consuming a stream

```python
import asyncio
from platform_messaging import StreamConsumer


async def message_handler(msg_id: str, msg_data: dict):
    print(f"Received {msg_id}: {msg_data}")


async def main():
    consumer = StreamConsumer(
        redis_url="redis://localhost:6379/0",
        stream_name="video-events",
        group_name="video-workers",
        consumer_name="worker-1",
        message_handler=message_handler,
    )

    await consumer.start()


asyncio.run(main())
```

## Serialization Behavior

The serializer will convert the following values into string-safe payloads before writing to Redis:

- `dict` and `list` → JSON string
- `datetime` → ISO 8601 string
- `uuid.UUID` → string form
- `Decimal` → string form
- `Enum` → enum value
- any other primitive value → string form

`None` values are skipped.

## Retry and DLQ Notes

The consumer supports:

- concurrent task limiting via `max_concurrent_tasks`
- blocking read timeout control via `block_timeout`
- retry count management via `max_retries`
- optional DLQ stream destination via `dlq_stream`

If a message fails repeatedly beyond the configured retry limit, it is moved to the DLQ stream.

## Notes

- This SDK currently targets Redis Streams-backed asynchronous message processing.
- Make sure the Redis server is reachable from the service using the provided `redis_url`.
- Consumer groups are created automatically if they do not exist.
