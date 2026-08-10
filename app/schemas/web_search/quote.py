from __future__ import annotations

from pydantic import BaseModel, Field


class WebQuoteResult(BaseModel):
    text: str = Field(..., min_length=1)
    author: str | None = None
    book: str | None = None
    source: str | None = None
    url: str | None = None
    score: float | None = None


class WebQuoteSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    limit: int = Field(default=10, ge=1, le=50)
