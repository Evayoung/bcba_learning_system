# 01 — Setup and Project Structure

## Objective

Create a runnable FastHTML + FastStrap application with configuration, database setup, navigation, and a smoke test. Do not implement the entire product yet.

## Before coding

1. Inspect the repository and existing files.
2. Inspect `pyproject.toml` or requirements files.
3. Inspect how FastStrap is used in this repository and consult its docs: https://faststrap-org.github.io/Faststrap/
4. Reuse existing conventions if they are correct; do not replace working code just to match a preferred layout.
5. Confirm the installed FastHTML/FastStrap versions and their APIs before choosing imports or component signatures.

## Suggested structure

Adapt if the repo already has a better working structure:

```text
app/
  __init__.py
  main.py
  config.py
  db.py
  models/
  schemas/
  routes/
  services/
  templates/
  static/
tests/
docs/
scripts/
.env.example
README.md
```

## Requirements

- Use environment-based configuration.
- Create a local SQLite database by default.
- Keep route handlers thin; put business logic in services.
- Add a shared base layout and responsive navigation using FastStrap.
- Add placeholder routes for Dashboard, Learn, Practice, Progress, and Mock Exam.
- Add a health/smoke test that imports the application and verifies important routes.
- Include clear commands to install dependencies, run tests, and start the app.
- Do not add external infrastructure.

## Acceptance checks

- App starts from a documented command.
- Main routes return successfully.
- No secrets are required to view the shell/dashboard.
- Test suite passes.
- README describes the actual project, not aspirational features.
