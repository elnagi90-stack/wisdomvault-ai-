# WisdomVault AI

Foundation v1 is now a runnable baseline for the personal knowledge management platform.

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

Run the FastAPI app:

```bash
python -m app
```

Or on PowerShell:

```powershell
./scripts/start.ps1
```

Run tests:

```bash
pytest -q
```
