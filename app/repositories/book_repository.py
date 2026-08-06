from __future__ import annotations

from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.book import Book


class SupportsSession(Protocol):
    def __call__(self) -> Session: ...


class BookRepository:
    def __init__(self, session_factory: SupportsSession):
        self._session_factory = session_factory

    def create(self, book: Book) -> Book:
        with self._session_factory() as session:
            session.add(book)
            session.commit()
            session.refresh(book)
            return book

    def get_by_id(self, book_id: str) -> Book | None:
        with self._session_factory() as session:
            return session.get(Book, book_id)

    def list_all(self) -> list[Book]:
        with self._session_factory() as session:
            return list(session.scalars(select(Book)).all())

    def delete(self, book_id: str) -> bool:
        with self._session_factory() as session:
            book = session.get(Book, book_id)

            if book is None:
                return False

            session.delete(book)
            session.commit()
            return True

    def search(self, keyword: str) -> list[Book]:
        with self._session_factory() as session:
            stmt = select(Book).where(Book.title.ilike(f"%{keyword}%"))

            return list(session.scalars(stmt).all())
