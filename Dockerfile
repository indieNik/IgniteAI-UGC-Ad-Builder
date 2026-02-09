# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
# ffmpeg and imagemagick are required for moviepy
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    libsm6 \
    libxext6 \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    pkg-config \
    libcairo2-dev \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file (we assume we are building from root context)
# Copy requirements file (we assume we are building from root context)
COPY requirements.txt /app/requirements.txt

# Install python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire project
COPY . /app

# Create tmp directory and set permissions
RUN mkdir -p /app/tmp && chmod 777 /app/tmp

# Create a non-root user and switch to it (Good practice for Cloud Run)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# CHANGED: Cloud Run expects port 8080 (not 7860)
EXPOSE 8080

# Command to run the application
# Cloud Run provides PORT environment variable (defaults to 8080)
CMD ["sh", "-c", "uvicorn projects.backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
