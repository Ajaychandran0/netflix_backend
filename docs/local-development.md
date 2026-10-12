# Local development

## Prerequisites

- Docker Desktop or Docker Engine with Compose v2
- Node.js 20+ and npm
- Python 3.11–3.13 when running Python code outside Docker
- Git access to `netflix-platform-messaging-sdk`, referenced by Python dependencies

## Configuration

| File | Responsibility | Key categories |
| --- | --- | --- |
| `.env` | Compose bootstrap | ports, Postgres, MinIO, Docker target |
| `api-gateway/.env` | Gateway | gateway port, JWT secret, service URLs, internal key, Redis |
| `user-service/.env` | Identity | service port, database URL, JWT secret, Redis |
| `content-service/.env` | Content and storage | database, Redis streams, S3/MinIO endpoints and buckets |
| `video-processing-service/.env` | Job launching | Redis stream/group/consumer, Docker image/network |
| `video-transcoder/.env` | Worker runtime | Redis, S3 endpoint/credentials/buckets |
| `../netflix_frontend/.env` | Browser | `VITE_API_BASE_URL` |

For Compose, downstream URLs use service names such as `http://user-service:<port>`. Gateway and user service must use the same `JWT_SECRET`.

## Run locally

From `netflix_backend`:

```bash
docker compose up --build
```

From `netflix_frontend`:

```bash
npm install
npm run dev
```

The frontend normally runs on `http://localhost:5173`; its `VITE_API_BASE_URL` should target the gateway, commonly `http://localhost:3000`.

## Verify the flow

1. Register or sign in.
2. Use an `ADMIN` account to reach the upload workspace.
3. Submit a video and confirm the browser receives presigned URLs, then uploads parts directly to MinIO.
4. Inspect processor/transcoder logs for queue consumption and FFmpeg stages.
5. Confirm generated assets in MinIO and metadata/asset keys in PostgreSQL.
6. Refresh the public catalogue and start HLS playback.

## Commands and first checks

| Symptom | First check |
| --- | --- |
| Gateway returns `401` | Re-authenticate; confirm gateway/user-service `JWT_SECRET` match |
| Part upload fails | Presigned public endpoint and MinIO CORS |
| Job never starts | Processor logs, Redis group settings, Docker socket mount |
| Worker cannot reach MinIO | Docker-network endpoint and transcoder S3 config |
| HLS will not play | Master playlist, public endpoint, generated segments |

Useful Compose commands:

```bash
docker compose logs -f content-service
docker compose up --build api-gateway
docker compose down
```

`docker compose down -v` also deletes local Postgres and MinIO volumes; use it only for an intentional clean reset.
