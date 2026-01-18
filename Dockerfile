# Use official slim Python image
FROM python:3.11-slim

# Avoid bytecode creation and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build deps for any native extensions (psycopg2, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install -r /app/requirements.txt

# Copy repository
COPY . /app

# Default port and command (Railway provides $PORT)
ENV PORT=8000

EXPOSE ${PORT}

# Use shell form to allow shell expansion of $PORT
CMD sh -c "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
