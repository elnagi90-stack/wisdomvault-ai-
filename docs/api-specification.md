# API Specification

## Versioning
All APIs must be versioned under /api/v1/.

## Core Endpoints
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/me
- GET /api/v1/books
- POST /api/v1/books
- GET /api/v1/books/{id}
- PUT /api/v1/books/{id}
- DELETE /api/v1/books/{id}
- GET /api/v1/quotes
- POST /api/v1/quotes
- GET /api/v1/notes
- POST /api/v1/notes
- POST /api/v1/uploads/images
- GET /api/v1/search

## API Rules
- Use consistent response envelopes
- Validate all inputs
- Return meaningful error codes
- Apply rate limiting on auth and write endpoints
