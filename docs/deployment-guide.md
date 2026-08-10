# Deployment Guide

## Environments
- Development: SQLite, local FastAPI, local storage
- Testing: pytest, temporary DB, mock secrets
- Production: PostgreSQL, Docker, managed secrets, reverse proxy

## Production Checklist
- Set strong JWT secrets
- Configure PostgreSQL connection string
- Set CORS origins explicitly
- Enable HTTPS and security headers
- Run migrations before deployment
- Enable observability and structured logging

## Docker
- Build: docker build -t wisdomvault-ai .
- Run: docker run -p 8000:8000 --env-file .env wisdomvault-ai
