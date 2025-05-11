# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
  # && apt-get install -y build-essential curl netcat \
  && apt-get clean

# Install pipenv or poetry if you're using it (optional)

# Copy dependency files
COPY ./requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . /app/

# Expose port (default FastAPI/uvicorn port)
EXPOSE 3002

# Run the app
CMD ["python", "main.py"]
