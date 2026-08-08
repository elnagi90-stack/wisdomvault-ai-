from __future__ import annotations

import json

from app.models.quote import Quote
from app.repositories.quote_repository import (
    QuoteRepository,
    SupportsSession,
)


_embedding_service = None
_embedding_unavailable = False


def _encode(text: str):
    """Best-effort embedding lookup."""
    global _embedding_service, _embedding_unavailable

    if _embedding_unavailable:
        return None

    if _embedding_service is None:
        try:
            from app.ai.embedding_service import EmbeddingService

            _embedding_service = EmbeddingService()
        except Exception:
            _embedding_unavailable = True
            return None

    try:
        return _embedding_service.encode_one(text)
    except Exception:
        return None


def _get_faiss_manager():
    try:
        from app.vector.faiss_manager import FaissManager

        return FaissManager()
    except Exception:
        return None


def _index_in_faiss(quote_id: str, vector) -> None:
    try:
        manager = _get_faiss_manager()

        if manager is None:
            return

        manager.add(
            quote_id,
            vector,
        )
    except Exception:
        pass


def _remove_from_faiss(quote_id: str) -> None:
    try:
        manager = _get_faiss_manager()

        if manager is None:
            return

        manager.remove(quote_id)
    except Exception:
        pass


class QuoteService:
    def __init__(
        self,
        repository: QuoteRepository | None = None,
        session_factory: SupportsSession | None = None,
    ) -> None:
        if repository is not None:
            self.repository = repository
        elif session_factory is not None:
            self.repository = QuoteRepository(
                session_factory=session_factory
            )
        else:
            raise TypeError(
                "Either repository or session_factory must be provided"
            )

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

        vector = _encode(text)

        quote.embedding = (
            json.dumps(vector.tolist())
            if vector is not None
            else None
        )

        quote = self.repository.create(quote)

        if vector is not None:
            _index_in_faiss(
                quote.id,
                vector,
            )

        return quote

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

    def update_quote(
        self,
        quote_id: str,
        payload,
    ) -> Quote | None:
        fields = payload.model_dump(
            exclude_unset=True
        )

        if "text" in fields:
            if (
                not fields["text"]
                or not fields["text"].strip()
            ):
                raise ValueError(
                    "Quote text cannot be empty."
                )

            fields["text"] = fields["text"].strip()

            vector = _encode(fields["text"])

            if vector is not None:
                fields["embedding"] = json.dumps(
                    vector.tolist()
                )

                _remove_from_faiss(quote_id)

                updated = self.repository.update(
                    quote_id,
                    **fields,
                )

                if updated is not None:
                    _index_in_faiss(
                        quote_id,
                        vector,
                    )

                return updated

            fields["embedding"] = None
            _remove_from_faiss(quote_id)

        if not fields:
            return self.repository.get_by_id(quote_id)

        return self.repository.update(
            quote_id,
            **fields,
        )

    def delete_quote(
        self,
        quote_id: str,
    ) -> bool:
        deleted = self.repository.delete(
            quote_id
        )

        if deleted:
            _remove_from_faiss(
                quote_id
            )

        return deleted

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
        return self.repository.by_book(
            book_id
        )

    def add_tag_to_quote(
        self,
        quote_id: str,
        tag_id: str,
    ) -> Quote | None:
        return self.repository.add_tag(
            quote_id,
            tag_id,
        )

    def remove_tag_from_quote(
        self,
        quote_id: str,
        tag_id: str,
    ) -> Quote | None:
        return self.repository.remove_tag(
            quote_id,
            tag_id,
        )

    def get_quotes_by_tag(
        self,
        tag_name: str,
    ) -> list[Quote]:
        return self.repository.by_tag(
            tag_name
        )

    def set_favorite(
        self,
        quote_id: str,
        is_favorite: bool = True,
    ) -> Quote | None:
        return self.repository.set_favorite(
            quote_id,
            is_favorite,
        )
