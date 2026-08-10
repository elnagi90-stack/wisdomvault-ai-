# WisdomVault AI

Foundation v1 is now a runnable baseline for the personal knowledge management platform.

## What's changed (quick)
- Added CORS configuration and optional simple API key protection for write endpoints.
- Included a minimal Alembic setup (alembic/) to manage database migrations.
- Added CI workflow for tests and linters.
- Added LICENSE and CONTRIBUTING guidance.
- Expanded README with detailed run & environment instructions.

## Structure

- `app/` contains the application package.
- `app/core/` contains configuration and logging helpers.
- `app/interfaces/` contains abstraction layers for AI, storage, OCR, and search.
- `tests/` contains the initial regression tests.
- `storage/` contains local data directories.

## Development

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Copy the environment example and adjust values as needed:

```bash
copy .env.example .env
```

Set the important environment variables in `.env` (examples):

```text
# Application
APP_NAME=WisdomVault AI
APP_ENV=development
DEBUG=true

# Database (SQLite default)
DATABASE_ENGINE=sqlite
DATABASE_URL=sqlite:///storage/database.db

# OpenAI (if using AI features)
OPENAI_API_KEY=sk-...

# Telegram bot (optional)
TELEGRAM_BOT_TOKEN=...

# CORS (defaults to allow all). To restrict, set:
CORS_ALLOW_ALL=true
# or to use allowed origins list, set to false and provide a comma-separated list:
# ALLOWED_ORIGINS=https://example.com,https://app.example.com

# Optional API key to protect write endpoints
API_KEY=
```

Notes:
- If you want to restrict CORS, set `CORS_ALLOW_ALL=false` and populate `ALLOWED_ORIGINS`.

## Database migrations

The repository includes a minimal Alembic setup. To initialize and run migrations:

```bash
alembic upgrade head
```

## Run the app

```bash
python -m app
```

Or on PowerShell:

```powershell
./scripts/start.ps1
```

Open http://127.0.0.1:8000/ui for a small browser UI.

## Tests & CI

Run tests:

```bash
pytest -q
```

This repo includes a GitHub Actions workflow that runs tests, ruff, black (check), and mypy on push/PR.
