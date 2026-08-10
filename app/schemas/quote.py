from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class QuoteBase(BaseModel):
    text: str = Field(..., min_length=1)

    book_id: str | None = None

    page_number: int | None = Field(default=None, ge=1)

    chapter: str | None = None

    language: str = "ar"

    notes: str | None = None

    rating: int = Field(default=0, ge=0, le=5)

    is_favorite: bool = False


class QuoteCreate(QuoteBase):
    pass


class QuoteUpdate(BaseModel):
    text: str | None = None
    book_id: str | None = None
    page_number: int | None = None
    chapter: str | None = None
    language: str | None = None
    notes: str | None = None
    rating: int | None = None
    is_favorite: bool | None = None


class QuoteResponse(QuoteBase):
    id: str

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


embedding: str | None = None
