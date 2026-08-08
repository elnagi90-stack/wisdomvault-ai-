from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.quote_tag import quote_tags

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.category import Category
    from app.models.tag import Tag

class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    book_id: Mapped[str | None] = mapped_column(
        ForeignKey("books.id"),
        nullable=True,
    )

    category_id: Mapped[str | None] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True,
    )

    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    chapter: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    language: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    rating: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    is_favorite: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    embedding: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    notion_page_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    book: Mapped[Book | None] = relationship(
        back_populates="quotes",
    )

    category: Mapped[Category | None] = relationship(
        back_populates="quotes",
    )

    tags: Mapped[list[Tag]] = relationship(
        secondary=quote_tags,
        back_populates="quotes",
    )
