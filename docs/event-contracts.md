# Event contracts and media pipeline

## Streams

| Stream | Producer | Consumer | Purpose |
| --- | --- | --- | --- |
| `video:processing:stream` | Content Service | Video Processing Service | A completed multipart source is ready for a worker |
| `video:events:stream` | Video Transcoder | Content Service | Persist lifecycle, stage, completion, and failure state |

Both consumers use Redis consumer groups. Consumer/group names and stream names are environment-configurable.

## Processing job

After a multipart upload completes, Content Service publishes a job with these meaningful fields:

```json
{
  "video_id": "uuid",
  "attempt_id": "uuid",
  "upload_path": "uploads/<uuid>_source.mp4",
  "user_id": "uuid",
  "title": "Demo video",
  "thumbnail_object_key": null
}
```

The processing service validates the event and starts `transcoder-<video-id>-<attempt-id>`, passing `VIDEO_ID`, `PROCESSING_ATTEMPT_ID`, and `UPLOAD_PATH` as environment variables.

Each processing job also carries an `attempt_id`. The container name includes both the video and attempt IDs, so redelivery of the same job cannot start a second container. A retry is a new attempt with a new ID.

## Domain events

Every lifecycle event includes `event_type`, `event_id`, `attempt_id`, and an `event_sequence`, in addition to its event payload. Transcoder events use a monotonically increasing sequence starting at 1. A launch-failure event from the video-processing service uses sequence 0, reserved for a failure before the transcoder starts.

| Event type | Payload | Content-service effect |
| --- | --- | --- |
| `VIDEO_PROCESSING_STARTED` | `video_id` | Mark video `PROCESSING` and record start time |
| `VIDEO_PROCESSING_STAGE_CHANGED` | `video_id`, `current_stage` | Update `current_stage` |
| `VIDEO_PROCESSING_COMPLETED` | asset keys, duration, dimensions, file size, MIME type | Mark completed and persist playback/metadata fields |
| `VIDEO_PROCESSING_FAILED` | `video_id`, stage, error | Transcoder failed; mark failed and persist error |
| `VIDEO_PROCESSING_LAUNCH_FAILED` | `video_id`, error | Video-processing service could not launch the transcoder; mark queued video failed without setting a processing start time |

## Processing stages

```mermaid
flowchart LR
    A[DOWNLOADING\n1–5%] --> B[EXTRACTING_METADATA\n5–10%]
    B --> C[TRANSCODING\n10–85%]
    C --> D[GENERATING_PLAYLIST\n85–90%]
    D --> E[GENERATING_THUMBNAIL\n90–93%]
    E --> F[UPLOADING_ASSETS\n93–98%]
    F --> G[CLEANUP\n98–100%]
```

The worker stores progress in an attempt-scoped Redis hash keyed as `video:progress:<video-id>:<attempt-id>`. Late progress from an older run cannot overwrite the current run. The default hash TTL is one hour; terminal status has a ten-minute TTL. The protected content endpoint `/api/content/videos/:videoId/progress` reads the hash for the video's current attempt and owning user.

Content Service locks the video row while handling a lifecycle event and applies only events for the current attempt whose sequence is newer than the last applied sequence. This sequence high-water mark suppresses duplicate and out-of-order deliveries; `event_id` is retained for tracing, not deduplication. Delayed events from previous attempts are ignored. A stage or completion event can establish the processing start time if it is the first accepted event. Launch failures only transition a still-queued video to `FAILED` and do not set `processing_started_at`.

## HLS output

The transcoder creates five variants:

| Variant | Scale | Video bitrate |
| --- | --- | --- |
| 240p | 426×240 | 400k |
| 360p | 640×360 | 800k |
| 480p | 854×480 | 1400k |
| 720p | 1280×720 | 2800k |
| 1080p | 1920×1080 | 5000k |

Each variant has an `index.m3u8` playlist and HLS `.ts` segments. The master playlist references variants, and `poster.jpg` is captured at 20% of source duration. Assets are uploaded to the video and thumbnail buckets respectively.

## Reliability considerations

- Upload completion updates the database and creates a `video:processing:stream` outbox record in one transaction. The relay retries Redis publication with backoff; if Redis accepts a message but the database commit is lost, at-least-once delivery is safe because the worker launch is attempt-idempotent.
- Lifecycle events are fenced by attempt ID and sequence. Worker launch retries that exhaust their retry budget emit a distinct launch-failure event; transcoder failures use `VIDEO_PROCESSING_FAILED`.
- `auto_remove=False` leaves worker containers available for inspection but needs a cleanup/reconciliation policy.
- The shared Redis Stream consumer moves repeatedly failing messages to its dead-letter stream. Dead-letter inspection/replay, worker crash reconciliation, container timeout enforcement, and cleanup remain operational follow-ups.
- Progress events are throttled by a percentage threshold and a five-second interval to avoid excessive Redis writes.
