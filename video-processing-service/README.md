# Video Processing Service

This service is the bridge between an uploaded source object and an isolated FFmpeg worker. It consumes video-processing jobs from Redis Streams and starts an attempt-scoped `video-transcoder` Docker container. Redelivery uses the same attempt-specific container name and will not launch a second worker.

## Runtime responsibilities

1. Join a configured Redis consumer group on `VIDEO_PROCESSING_STREAM`.
2. Validate a job containing `video_id` and `upload_path`.
3. Create a named `transcoder-<video-id>` container.
4. Pass `VIDEO_ID` and `UPLOAD_PATH` into the worker environment.
5. Log launch success/failure and let the stream consumer retry failures.

It does **not** transcode media, write video metadata, or upload assets. Those responsibilities remain in the disposable transcoder and Content Service.

## Configuration

| Variable | Meaning |
| --- | --- |
| `REDIS_URL` | Redis endpoint, including database number |
| `VIDEO_PROCESSING_STREAM` | Upload-completion job stream |
| `REDIS_CONSUMER_GROUP` / `REDIS_CONSUMER_NAME` | Consumer-group identity |
| `DOCKER_TRANSCODER_IMAGE` | Image used for spawned workers |
| `DOCKER_NETWORK` | Network that lets workers reach Redis and MinIO |
| `PROCESSING_TIMEOUT` | Intended job timeout configuration; not yet enforced by the launcher |

## Local runtime

Docker Compose mounts `/var/run/docker.sock` so this service can start worker containers. That grants high privilege on the host and is appropriate only for local development. Use a constrained job runner/orchestrator in production.

```bash
# Run with the complete platform
docker compose up --build video-processing-service
```

See the system [event contracts](../docs/event-contracts.md) for event payloads.
