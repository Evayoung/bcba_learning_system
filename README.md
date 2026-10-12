# BCBA AI Learning Assistant

An AI-powered study companion for the BCBA exam, built on the **PTB ABA Exam Study Manual (6th Edition)**. Combines SQLite FTS5 RAG retrieval with Google Gemini / Groq LLMs to ground every answer in the actual book.

> **Stack:** FastHTML · FastStrap · HTMX · SQLAlchemy · SQLite FTS5 · Uvicorn

---

## Features

| Module | What it does |
|--------|--------------|
| **AI Tutor** | Ask any BCBA topic — answers are grounded in 512 indexed manual chunks with printed page citations |
| **Practice** | Spaced-repetition MCQ practice across all 9 BACB domains |
| **Mock Exam** | Timed 130-question simulation with full scoring |
| **Progress** | Domain accuracy heat-map and mastery-stage tracking |
| **Settings** | In-app API key management (no restart needed), account credential update |
| **Auth** | Login-protected; default credentials updatable from the Settings page |

---

## Quick Start (Local)

### Prerequisites
- Python 3.13
- Shared virtualenv at `../  .venv` **or** create a project-local one (see below)

```powershell
# Create & activate venv
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and populate secrets
copy .env.example .env
# → Edit .env: set GEMINI_API_KEY and/or GROQ_API_KEY

# Run the app (auto-seeds DB on first start)
python main.py
# Open http://localhost:5001
```

**Default login:** `student@bcba.prep` / `bcba2026password`  
Change both from **Settings → Account Credentials** once logged in.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes* | Google Gemini API key |
| `GROQ_API_KEY` | Yes* | Groq API key (Llama fallback) |
| `SESSION_SECRET` | Recommended | FastHTML session signing secret (auto-generated if absent) |
| `DATABASE_URL` | No | SQLite path (default: `sqlite:///data/bcba_assistant.db`) |
| `PORT` | No | Server port (default: `5001` local, `$PORT` in cloud) |

*At least one AI provider key is required.

---

## Deployment

### FastAPI Cloud (Primary)

The project is configured for [FastAPI Cloud](https://fastapicloud.com) via [`pyproject.toml`](pyproject.toml).

```bash
# 1. Install the FastAPI Cloud CLI (already bundled in fastapi[standard])
pip install "fastapi[standard]"

# 2. Log in
fastapi login

# 3. Set env vars in the FastAPI Cloud dashboard:
#    GEMINI_API_KEY, GROQ_API_KEY, SESSION_SECRET

# 4. Deploy (run from the project root)
fastapi deploy
```

The `[tool.fastapi]` section in `pyproject.toml` points the CLI at `app.main:app`.  
On first boot the app automatically seeds 512 content chunks from `data/processed/seed_content_chunks.json`.

> **SQLite persistence:** set `DATABASE_URL` to a persistent volume path in the platform's environment settings to keep the DB across redeploys.

### Docker (alternative)
```bash
docker build -t bcba-learning .
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e SESSION_SECRET=your_secret \
  bcba-learning
```

### Heroku / Railway (alternative)
```bash
# Uses Procfile — set env vars in the platform dashboard, then:
git push heroku main
```

---

## Repository Layout

```
app/                    FastHTML + FastStrap application
  main.py               App factory, Beforeware auth guard, startup hooks
  models/               SQLAlchemy models (Domain, Task, ContentChunk, Question, User…)
  routes/               Route handlers (auth, learn, practice, progress, mock, settings)
  services/             Business logic (RAG retrieval, AI tutor, auth, settings, ingestion)
  presentation/         Pages and shell (FastStrap components)
assets/css/             Custom CSS (fixed sidebar, markdown rendering, scrollbar styles)
tests/                  pytest suite (61 tests, 1 skip)
docs/                   Build kit, CODEX tasks, curriculum spec
data/
  processed/
    seed_content_chunks.json  ← committed; 512 indexed PTB manual chunks
.env.example            Template for secrets
requirements.txt        Production Python dependencies
pyproject.toml          FastAPI Cloud entrypoint config + project metadata
Dockerfile              Container build (FastAPI Cloud + Docker platforms)
Procfile                Heroku / Railway process definition
```

---

## RAG Architecture

The tutor uses **SQLite FTS5 sparse retrieval (Option A)**:

1. **Retrieval** — Given a study task (`B.4`) or free-text query, FTS5 + task/domain metadata filters fetch the top-*k* manual chunks (≤ 2 ms, fully local).
2. **Augmented Generation** — Chunks + printed page numbers are injected into the LLM system prompt; the model answers *only* from retrieved text.

No vector embeddings, no external vector DB, no extra API costs for retrieval.

---

## Running Tests

```powershell
.venv\Scripts\python.exe -m pytest -v
# 61 passed, 1 skipped (live Gemini test skips on quota/invalid key)
```

---

## License & Copyright Notice

This is a personal study tool. The PTB ABA Exam Study Manual is copyrighted material — extracted text chunks are used solely for personal study and are never redistributed. This repository does not contain the source PDF or any raw OCR page images.
