# Software Requirements Specification (SRS)

## 1. Product Overview
WisdomVault AI is a personal knowledge management platform intended to become a long-term knowledge assistant for books, quotes, notes, files, images, flashcards, and AI-assisted workflows.

## 2. Goals
- Provide a secure, maintainable, multi-user knowledge workspace.
- Support CRUD operations for core knowledge assets.
- Provide search, categorization, favorites, and reading progress.
- Prepare the architecture for future AI and OCR expansion without rework.

## 3. Scope
### In Scope for MVP
- Authentication
- Dashboard
- Books CRUD
- Quotes CRUD
- Notes CRUD
- Image upload
- Search
- Categories
- Tags
- Favorites
- Responsive UI

### Out of Scope for MVP
- OCR
- AI
- Semantic Search
- Flashcards
- Telegram integration

## 4. Functional Requirements
- Users can register and authenticate.
- Authenticated users can create, read, update, and delete books, quotes, notes.
- Users can upload and manage images/files.
- Users can assign categories and tags.
- Users can mark items as favorites.
- Users can search across their knowledge base.
- The system must expose versioned APIs under /api/v1/.

## 5. Non-Functional Requirements
- Security: JWT, password hashing, rate limiting, CORS, secrets in .env.
- Quality: type hints, docstrings, tests, linting, mypy.
- Performance: pagination, indexes, avoidance of N+1 queries.
- Reliability: structured logging, global error handling, migrations via Alembic.

## 6. Assumptions and Constraints
- Python 3.13
- FastAPI + SQLAlchemy 2.x + PostgreSQL for production
- SQLite for development only
