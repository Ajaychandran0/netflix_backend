FROM python:3.11-slim


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# System dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

# Copy poetry files if using poetry
COPY pyproject.toml poetry.lock* /app/
RUN pip install --upgrade pip && pip install poetry
RUN poetry install --no-root --only main

# Copy app code
COPY . /app

CMD ["python", "-m", "app.main"]