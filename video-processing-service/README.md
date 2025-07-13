# Video Processing Service

This service is a core component of the Netflix backend system, responsible for processing video-related events, launching processing containers, and integrating with Redis streams for event-driven workflows.

## Features

- **Event-Driven Processing:** Consumes video events from Redis streams for scalable, asynchronous processing.
- **Containerized Workflows:** Launches processing containers to handle video processing tasks.
- **Configurable & Extensible:** Centralized configuration and logging for easy management and debugging.

## Project Structure

```
video-processing-service/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Entry point for the service
│   ├── consumer/
│   │   └── redis_stream_consumer.py   # Consumes video events from Redis streams
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   └── logger.py            # Logging setup
│   ├── processor/
│   │   └── container_launcher.py # Launches containers for video processing
│   └── schemas/
│       └── video_event.py       # Pydantic schemas for video event data
├── Dockerfile                   # Containerization setup
├── poetry.lock                  # Poetry lock file for dependencies
├── pyproject.toml               # Project metadata and dependencies
└── README.md                    # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.8+
- [Poetry](https://python-poetry.org/docs/)
- Docker (for containerized processing)
- Redis (for event streaming)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd video-processing-service
   ```
2. **Install dependencies:**
   ```bash
   poetry install
   ```
3. **Configure environment variables:**
   - Copy `.env.example` to `.env` and update as needed (if applicable).

### Running the Service

#### Locally

```bash
poetry run python -m app.main
```

#### With Docker

```bash
docker build -t video-processing-service .
docker run --env-file .env video-processing-service
```

## Configuration

Configuration is managed via `app/core/config.py`. Update this file or use environment variables to set Redis connection details, container settings, and other service parameters.

## Key Components

- **`app/main.py`**: Service entry point; initializes consumers and processing logic.
- **`app/consumer/redis_stream_consumer.py`**: Listens to Redis streams for video events and triggers processing.
- **`app/processor/container_launcher.py`**: Handles launching and managing processing containers.
- **`app/schemas/video_event.py`**: Defines the structure of video event data using Pydantic models.
- **`app/core/config.py`**: Centralized configuration management.
- **`app/core/logger.py`**: Logging setup for the service.

## Development

- Linting: `poetry run flake8 app/`
- Formatting: `poetry run black app/`
- Testing: (Add tests and run with your preferred test runner)


## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.

## Contact

For questions or support, please contact the maintainer.
