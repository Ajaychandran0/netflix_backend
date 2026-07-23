# Use a slim base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml poetry.lock* /app/

# Install Poetry
RUN pip install --upgrade pip && pip install poetry

# Install Python dependencies
RUN poetry install --no-root --only main && \
    rm -rf /root/.cache/pypoetry /root/.cache/pip

# Copy app code
COPY . /app

# Default command
CMD ["python", "-m", "app.main"]
