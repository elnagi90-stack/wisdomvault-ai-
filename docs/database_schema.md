# WisdomVault AI - Database Schema (Version 1.0)

## الهدف

تصميم قاعدة بيانات قابلة للتوسع تدعم:

- Quotes
- Books
- Notes
- Flashcards
- OCR
- AI
- Semantic Search
- Telegram Bot
- Web App
- Mobile App

---

# Design Principles

- UUID Primary Keys
- Soft Delete
- Created / Updated timestamps
- Foreign Keys
- Indexes
- Many-to-Many Relations
- Production Ready

---

# Entity Relationship Diagram

User
├── Books
├── Quotes
├── Notes
└── Flashcards

Book
└── Quotes

Category
└── Quotes

Quote
├── Images
└── Tags

Tag
└── Quotes

---

# Users

| Column | Type |
|---------|------|
| id | UUID |
| username | String(100) |
| email | String(255) |
| password_hash | String |
| is_active | Boolean |
| created_at | DateTime |
| updated_at | DateTime |

---

# Books

| Column | Type |
|---------|------|
| id | UUID |
| user_id | UUID |
| title | String(255) |
| author | String(255) |
| isbn | String(30) |
| description | Text |
| language | String(20) |
| total_pages | Integer |
| cover_image | String |
| reading_status | Enum |
| rating | Integer |
| created_at | DateTime |
| updated_at | DateTime |
| deleted_at | DateTime |

---

# Quotes

| Column | Type |
|---------|------|
| id | UUID |
| user_id | UUID |
| book_id | UUID (Nullable) |
| category_id | UUID (Nullable) |
| title | String(255) |
| text | Text |
| author | String(255) |
| source | String(255) |
| language | String(20) |
| page_number | Integer |
| notes | Text |
| is_favorite | Boolean |
| created_at | DateTime |
| updated_at | DateTime |
| deleted_at | DateTime |

---

# Categories

| Column | Type |
|---------|------|
| id | UUID |
| name | String(100) |
| description | Text |

---

# Tags

| Column | Type |
|---------|------|
| id | UUID |
| name | String(100) |

---

# QuoteTags

Many-to-Many

| Column | Type |
|---------|------|
| quote_id | UUID |
| tag_id | UUID |

Primary Key:

- quote_id
- tag_id

---

# QuoteImages

| Column | Type |
|---------|------|
| id | UUID |
| quote_id | UUID |
| image_path | String |
| ocr_text | Text |
| created_at | DateTime |

---

# Notes

| Column | Type |
|---------|------|
| id | UUID |
| user_id | UUID |
| title | String(255) |
| content | Text |
| created_at | DateTime |
| updated_at | DateTime |
| deleted_at | DateTime |

---

# Flashcards

| Column | Type |
|---------|------|
| id | UUID |
| user_id | UUID |
| question | Text |
| answer | Text |
| ease_factor | Float |
| interval_days | Integer |
| repetitions | Integer |
| next_review | DateTime |
| created_at | DateTime |
| updated_at | DateTime |

---

# Search

The search system must support:

- Quote text
- Book title
- Author
- OCR text
- Notes
- Tags

---

# Future Modules

- AI
- OCR
- Semantic Search
- Daily Wisdom
- Telegram Bot
- Web Dashboard
- Mobile Application