# ── BCBA AI Learning System — Dockerfile ─────────────────────────────────────
FROM python:3.13-slim

# Prevent .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install git (needed for faststrap editable install from GitHub)
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer cache friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/
COPY assets/ ./assets/
COPY data/processed/seed_content_chunks.json ./data/processed/seed_content_chunks.json
COPY main.py .
COPY .env.example .

# Create runtime data dirs (DB lives here at runtime)
RUN mkdir -p data/processed

EXPOSE $PORT

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
