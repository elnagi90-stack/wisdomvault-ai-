from __future__ import annotations

import json

from app.ai.embedding_service import EmbeddingService
from app.models.quote import Quote
from app.repositories.quote_repository import (
    QuoteRepository,
    SupportsSession,
)


class QuoteService:
    def __init__(
        self,
        repository: QuoteRepository | None = None,
        session_factory: SupportsSession | None = None,
    ) -> None:
        if repository is not None:
            self.repository = repository
        elif session_factory is not None:
            self.repository = QuoteRepository(session_factory=session_factory)
        else:
            raise TypeError("Either repository or session_factory must be provided")

    def create_quote(
        self,
        *,
        text: str,
        book_id: str | None = None,
        page_number: int | None = None,
        chapter: str | None = None,
        language: str = "ar",
        notes: str | None = None,
        rating: int = 0,
        is_favorite: bool = False,
    ) -> Quote:
        if not text.strip():
            raise ValueError("Quote text cannot be empty.")

        quote = Quote(
            text=text.strip(),
            book_id=book_id,
            page_number=page_number,
            chapter=chapter,
            language=language,
            notes=notes,
            rating=rating,
            is_favorite=is_favorite,
        )

        vector = EmbeddingService().encode_one(text)
        quote.embedding = json.dumps(vector.tolist())

        return self.repository.create(quote)

    def list_quotes(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Quote]:
        return self.repository.list_all(
            limit=limit,
            offset=offset,
        )

    def get_quote(
        self,
        quote_id: str,
    ) -> Quote | None:
        return self.repository.get_by_id(quote_id)

    def delete_quote(
        self,
        quote_id: str,
    ) -> bool:
        return self.repository.delete(quote_id)

    def search_quotes(
        self,
        keyword: str,
        limit: int = 50,
    ) -> list[Quote]:
        return self.repository.search_text(
            keyword=keyword,
            limit=limit,
        )

    def get_random_quote(
        self,
    ) -> Quote | None:
        return self.repository.random_quote()

    def get_favorites(
        self,
    ) -> list[Quote]:
        return self.repository.favorites()

    def get_quotes_by_book(
        self,
        book_id: str,
    ) -> list[Quote]:
        return self.repository.by_book(book_id)

    def get_quotes_by_tag(
        self,
        tag_name: str,
    ) -> list[Quote]:
        return self.repository.by_tag(tag_name)
