# ── BCBA AI Learning System — Dockerfile ─────────────────────────────────────
# Used by FastAPI Cloud (and Docker-based platforms) for containerized deploys.
FROM python:3.13-slim

# Prevent .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install git (needed for faststrap editable install from GitHub)
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from pyproject.toml
COPY pyproject.toml .
COPY requirements.txt .
COPY vendor/ ./vendor/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/
COPY assets/ ./assets/
COPY data/processed/seed_content_chunks.json ./data/processed/seed_content_chunks.json
COPY data/processed/source_quality_manifest.json ./data/processed/source_quality_manifest.json
COPY data/processed/tco_6th_edition_tasks.json ./data/processed/tco_6th_edition_tasks.json
COPY data/processed/adapted_practice_questions.py ./data/processed/adapted_practice_questions.py
COPY main.py .
COPY .env.example .

# Create runtime data dirs (SQLite DB lives here at runtime)
RUN mkdir -p data/processed

EXPOSE $PORT

# FastAPI Cloud uses the [tool.fastapi] entrypoint from pyproject.toml;
# for vanilla Docker, uvicorn is called directly.
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
