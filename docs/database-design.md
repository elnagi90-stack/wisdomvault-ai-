# Database Design

## 1. Core Design Goals
- Support scalable multi-tenant-ready data model
- Preserve user ownership and referential integrity
- Prepare for future search and analytics features

## 2. Core Entities
- users
- books
- quotes
- notes
- images
- files
- flashcards
- tags
- categories
- favorites
- reading_progress
- daily_wisdom

## 3. Key Relationships
- users 1:N books, quotes, notes, files, images
- books N:M tags/categories
- notes N:M tags/categories
- favorites link users to any content type
- reading_progress links users to books or notes

## 4. Design Rules
- Use UUID primary keys for cross-system portability where possible
- Add indexes on foreign keys and frequently queried columns
- Use soft delete where appropriate for auditability
- Avoid N+1 by using eager loading and explicit joins

## 5. Migration Strategy
- Alembic only
- Every schema change requires a migration
- SQLite for local development, PostgreSQL in production
