from __future__ import annotations

from app.models.book import Book
from app.repositories.book_repository import (
    BookRepository,
    SupportsSession,
)


class BookService:
    def __init__(
        self,
        repository: BookRepository | None = None,
        session_factory: SupportsSession | None = None,
    ) -> None:
        if repository is not None:
            self.repository = repository
        elif session_factory is not None:
            self.repository = BookRepository(session_factory=session_factory)
        else:
            raise TypeError("Either repository or session_factory must be provided")

    def create_book(
        self,
        *,
        title: str,
        author_id: str | None = None,
        publisher: str | None = None,
        publication_year: int | None = None,
        isbn: str | None = None,
        language: str | None = None,
        cover_image: str | None = None,
    ) -> Book:

        if not title.strip():
            raise ValueError("Book title cannot be empty.")

        book = Book(
            title=title.strip(),
            author_id=author_id,
            publisher=publisher,
            publication_year=publication_year,
            isbn=isbn,
            language=language,
            cover_image=cover_image,
        )

        return self.repository.create(book)

    def list_books(self) -> list[Book]:
        return self.repository.list_all()

    def get_book(self, book_id: str) -> Book | None:
        return self.repository.get_by_id(book_id)

    def delete_book(self, book_id: str) -> bool:
        return self.repository.delete(book_id)

    def search_books(self, keyword: str) -> list[Book]:
        return self.repository.search(keyword)
