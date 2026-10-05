# Video Transcoder

The video transcoder is a short-lived worker started once per uploaded source video. It converts a source object into adaptive HLS media, generates a poster, uploads outputs to object storage, and reports state through Redis.

## Pipeline

1. Download source from the temporary object bucket.
2. Extract duration, MIME type, dimensions, and file-size metadata.
3. Transcode 240p, 360p, 480p, 720p, and 1080p HLS variants with FFmpeg.
4. Generate a master playlist and poster image.
5. Upload HLS files and poster to their configured buckets.
6. Publish processing-completed metadata, or a failure event with the active stage.
7. Remove temporary local files.

The full stage model, progress ranges, and event payloads are in [Event contracts](../docs/event-contracts.md).

## Inputs

The processor passes these dynamic container variables:

| Variable | Meaning |
| --- | --- |
| `VIDEO_ID` | Video record UUID |
| `UPLOAD_PATH` | Source-object key in the temporary bucket |

Static configuration supplies Redis and S3-compatible storage endpoints, credentials, bucket names, and the domain-event stream.

## Outputs

- Variant playlists and `.ts` segments in `S3_VIDEO_BUCKET`
- `master.m3u8` key stored on the video record
- `poster.jpg` in `S3_THUMBNAIL_BUCKET`
- Persisted metadata: duration, source dimensions, source size, MIME type
- `VIDEO_PROCESSING_*` events to `VIDEO_EVENTS_STREAM`

## Operational notes

Workers are deliberately disposable but currently use `auto_remove=False` to aid local inspection. Production should add time/memory/CPU limits, idempotency, cleanup/reconciliation, and a dead-letter strategy.
