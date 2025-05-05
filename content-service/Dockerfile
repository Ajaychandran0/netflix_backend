# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
  && apt-get install -y build-essential curl netcat \
  && apt-get clean

# Install pipenv or poetry if you're using it (optional)

# Copy dependency files
COPY pyproject.toml poetry.lock* requirements.txt* /app/

# Install Python dependencies
RUN pip install --upgrade pip \
  && if [ -f "requirements.txt" ]; then pip install -r requirements.txt; fi \
  && if [ -f "pyproject.toml" ]; then pip install .; fi

# Copy application code
COPY . /app

# Expose port (default FastAPI/uvicorn port)
EXPOSE 8000

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
