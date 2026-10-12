FROM python:3.11-slim


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy poetry files if using poetry
COPY pyproject.toml poetry.lock* /app/

RUN pip install --upgrade pip && \
    pip install --no-cache-dir poetry

RUN poetry install --no-root --only main && \
    rm -rf /root/.cache/pypoetry /root/.cache/pip
    
# Copy app code
COPY . /app

CMD ["python", "-m", "app.main"]