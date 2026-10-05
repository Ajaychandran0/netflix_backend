# API reference

Base URL: `http://localhost:3000` by default. The API gateway is the only browser-facing backend entry point.

## Response envelope

Successful service responses use this shape:

```json
{
  "message": "Human-readable result",
  "data": {},
  "statusCode": 200,
  "code": "MACHINE_READABLE_CODE"
}
```

Error responses are service-specific today. Normalizing error envelopes is a recommended follow-up.

## Authentication

Protected routes require:

```http
Authorization: Bearer <JWT>
```

The JWT is issued by the User Service and verified by the gateway. Public catalogue and playback routes do not require a token in the MVP because media is intentionally public for testing.

## Identity

### `POST /api/auth/register`

Creates a user and returns a JWT.

```json
{ "email": "viewer@example.com", "password": "a-strong-password" }
```

### `POST /api/auth/signin`

Authenticates a user and returns a JWT.

```json
{ "email": "viewer@example.com", "password": "a-strong-password" }
```

### `GET /api/users/profile` — protected

Returns the current user without the password hash.

### `PUT /api/users/profile` — protected

Updates `firstName` and/or `lastName`. Unsupported fields should not be assumed to persist.

## Catalogue and playback

### `GET /api/content/videos` — public

Returns completed videos only.

Query parameters:

| Parameter | Default | Meaning |
| --- | --- | --- |
| `page` | `1` | One-based page number |
| `page_size` | `20` | Maximum items returned |
| `search` | none | Case-insensitive title search |

Example `data`:

```json
{
  "items": [{
    "id": "uuid",
    "title": "Sample release",
    "thumbnail_url": "http://minio/.../poster.jpg",
    "duration_ms": 120000,
    "status": "COMPLETED",
    "created_at": "2026-10-01T00:00:00Z"
  }],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### `GET /api/content/videos/:videoId/playback` — public

Returns the public HLS master playlist location and an expiry timestamp. The expiry is metadata in the public-bucket MVP; it is not an access control mechanism until signed media URLs are introduced.

```json
{
  "playback_url": "http://minio/video-bucket/videos/<id>/master.m3u8",
  "expires_at": "2026-10-01T01:00:00Z"
}
```

## Upload and owner management

### `POST /api/content/initiate_upload` — protected

Creates a video/upload-session record and starts a multipart object-store upload.

```json
{
  "filename": "source.mp4",
  "title": "Demo video",
  "description": "Optional description",
  "total_parts": 12
}
```

The response returns `upload_id`, `video_id`, and ordered part records containing `part_number` and `presigned_url`. Upload each source chunk directly to the supplied URL with `PUT`; do not send file bytes through the gateway.

### `POST /api/content/complete_upload` — protected

Completes the multipart upload and queues video processing.

```json
{
  "video_id": "uuid",
  "upload_id": "object-store-upload-id",
  "parts": [
    { "part_number": 1, "etag": "etag-from-put-response" }
  ]
}
```

### `GET /api/content/videos/mine` — protected

Lists the caller's videos, including active and failed processing jobs. Each item has `status`, `current_stage`, optional `last_error`, thumbnail URL, duration, title, and description.

### `PUT /api/content/videos/:videoId` — protected

Updates the caller's own video title and/or description. The current content-service implementation requires the caller to have the `ADMIN` role.

```json
{ "title": "Updated title", "description": "Updated description" }
```

### `DELETE /api/content/videos/:videoId` — protected

Soft-deletes the caller's own video record. The current content-service implementation requires the caller to have the `ADMIN` role and does not yet delete object-store assets. Treat the request as destructive from a product perspective and add object lifecycle cleanup before production.

### `POST /api/content/cancel_upload` — incomplete

Present as a placeholder only. It does not yet abort object-store multipart uploads or update the database reliably.

## Frontend integration notes

- The frontend currently exposes uploading to `ADMIN` users, but the upload endpoints themselves are JWT-protected rather than role-enforced. Add server-side publisher authorization before treating this as a security boundary.
- Store the JWT locally only for this MVP; an httpOnly secure cookie is safer for a production browser application.
- Use an HLS-capable player. Safari can play HLS natively; other major browsers generally need `hls.js`.
- Poll `GET /videos/mine` while an upload is active. Redis carries more granular progress, but no browser progress endpoint exists yet.
