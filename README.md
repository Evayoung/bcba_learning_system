# BCBA AI Learning Assistant

An AI-powered study companion for the BCBA exam, built on the **PTB ABA Exam Study Manual (6th Edition)**. Combines SQLite FTS5 RAG retrieval with Google Gemini / Groq LLMs to ground every answer in the actual book.

> **Stack:** FastHTML · FastStrap · HTMX · SQLAlchemy · SQLite FTS5 · Uvicorn

---

## Features

| Module | What it does |
|--------|--------------|
| **AI Tutor** | Ask BCBA topics; the tutor retrieves source-verified manual chunks and displays printed-page citations |
| **Practice** | Practice with 13 adapted multiple-choice items based on manual concepts; they are not verbatim manual review questions |
| **Short Practice Set** | A 13-question, 60-minute activity from the current small adapted question pool; it is not a full exam simulation |
| **Progress** | Review attempt totals, accuracy, and domain summaries |
| **Settings** | Account credential updates and AI service availability |
| **Auth** | Private account seeded from operator secrets; no shared default login |

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
# Edit .env: keep APP_ENV=development, set APP_BASE_URL=http://localhost:5001,
# add a provider key, and set CANDIDATE_EMAIL/CANDIDATE_PASSWORD for first startup.

# Run the app (auto-seeds DB on first start)
python main.py
# Open http://localhost:5001
```

At startup, the app creates the first private account on an empty database from
`CANDIDATE_EMAIL`, `CANDIDATE_PASSWORD`, and optional `CANDIDATE_NAME`. Existing
accounts are not overwritten. For local use, set these in `.env` before starting.
The password must be at least 12 characters. Keep it in a secret manager and
share it with the candidate through a private channel.

You can also provision an account interactively from the project directory:

```powershell
python -m app.bootstrap_user
```

The command prompts for the email and password without echoing the password.
To reset an existing account, run `python -m app.bootstrap_user --reset user@example.com`.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes* | Google Gemini API key |
| `GROQ_API_KEY` | Yes* | Groq API key (Llama fallback) |
| `SESSION_SECRET` | Required in production | Random secret of at least 32 characters; local development generates an ephemeral value if omitted |
| `APP_ENV` | Required in production | Set to `production` to enforce production secret and HTTPS checks |
| `APP_BASE_URL` | Required in production | Public app URL; must start with `https://` in production |
| `CANDIDATE_EMAIL` | Required only for first account creation | Candidate's login email; used only when the database has no users |
| `CANDIDATE_PASSWORD` | Required only for first account creation | Initial password (at least 12 characters); used only when the database has no users |
| `CANDIDATE_NAME` | No | Display name for the first account |
| `DATABASE_URL` | No | SQLite path (default: `sqlite:///data/bcba_assistant.db`) |
| `PORT` | No | Server port (default: `5001` local, `$PORT` in cloud) |
| `LLM_PROVIDER` / `LLM_MODEL` | No | Recommended: `gemini` / `gemini-3.8-flash` |
| `GEMINI_API_KEY`, `GROQ_API_KEY`, `OPENROUTER_API_KEY` | One required for tutor | Provider credentials configured by the app owner, never in learner settings |

At least one tutor provider key is required for AI explanations. Practice works without it.

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
#    APP_ENV=production, APP_BASE_URL=https://your-app-domain,
#    SESSION_SECRET, CANDIDATE_EMAIL, CANDIDATE_PASSWORD,
#    and the selected provider key/model

# 4. Deploy (run from the project root)
fastapi deploy
```

The `[tool.fastapi]` section in `pyproject.toml` points the CLI at `app.main:app`.  
On first boot the app automatically seeds 512 content chunks from `data/processed/seed_content_chunks.json`, records their page-level status from `data/processed/source_quality_manifest.json`, and creates the first candidate from `CANDIDATE_EMAIL` and `CANDIDATE_PASSWORD`. Set `CANDIDATE_NAME` if you want a display name other than “BCBA Candidate”. The password must be at least 12 characters. These credentials are ignored once any account exists, so later deploys do not reset the candidate's password. The interactive `python -m app.bootstrap_user` command remains available for manual provisioning or password resets. Provider credentials are read only from deployment environment settings and are not editable in the learner interface.

To reset the candidate password later, use `python -m app.bootstrap_user --reset candidate@example.com` against the same database.

> **SQLite persistence:** SQLite is suitable for a small test, but the database file survives redeploys only if the platform keeps the exact file path on persistent storage. Confirm that `/data` is mounted persistently before relying on it for learner progress. FastAPI Cloud also offers managed Postgres integrations; this app currently uses SQLite FTS5 for search, so a Postgres switch requires adapting the search implementation first.

### Docker (alternative)
```bash
docker build -t bcba-learning .
docker run -p 8000:8000 \
  -e APP_ENV=production \
  -e APP_BASE_URL=https://your-app-domain \
  -e CANDIDATE_EMAIL=candidate@example.com \
  -e CANDIDATE_PASSWORD=replace_with_a_private_password \
  -e GEMINI_API_KEY=your_key \
  -e SESSION_SECRET=your_random_secret_at_least_32_characters \
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
    seed_content_chunks.json  ← committed; 512 source-verified PTB manual chunks
    source_quality_manifest.json ← page QA status and known question/source gaps
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
2. **Augmented Generation** — Verified chunks + printed page numbers are injected into the LLM system prompt; citations come from application metadata.

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
