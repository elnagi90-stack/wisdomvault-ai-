# Coding Standards

## 1. Python Requirements
- Python 3.13+
- Type hints on every function and method
- Public classes documented with docstrings
- No TODO, FIXME, or print()
- No global state
- No SQL inside routes
- No business logic inside controllers

## 2. Formatting and Quality
- black
- ruff
- mypy
- pre-commit

## 3. Testing
- pytest
- unit tests for business rules
- integration tests for persistence and API
- coverage target: >= 80%

## 4. Design Rules
- Favor composition over inheritance
- Use dependency injection
- Keep routes thin and declarative
- Prefer small, focused modules
