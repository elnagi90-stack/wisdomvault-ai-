from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


class BookBase(BaseModel):
    title: str
    author_id: uuid.UUID | None = None
    publisher: str | None = None
    publication_year: int | None = None
    isbn: str | None = None
    language: str | None = None
    cover_image: str | None = None


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = None
    author_id: uuid.UUID | None = None
    publisher: str | None = None
    publication_year: int | None = None
    isbn: str | None = None
    language: str | None = None
    cover_image: str | None = None


class BookResponse(BookBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
