from __future__ import annotations

from typing import Protocol

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.author import Author


class SupportsSession(Protocol):
    def __call__(self) -> Session: ...


class AuthorRepository:
    def __init__(self, session_factory: SupportsSession):
        self._session_factory = session_factory

    def create(self, author: Author) -> Author:
        with self._session_factory() as session:
            session.add(author)
            session.commit()
            session.refresh(author)
            return author

    def get_by_id(self, author_id: str) -> Author | None:
        with self._session_factory() as session:
            return session.get(Author, author_id)

    def get_by_name(self, name: str) -> Author | None:
        with self._session_factory() as session:
            stmt = select(Author).where(Author.name == name)
            return session.scalar(stmt)

    def list_all(self) -> list[Author]:
        with self._session_factory() as session:
            stmt = select(Author).order_by(Author.name)
            return list(session.scalars(stmt).all())

    def update(
        self,
        author_id: str,
        **fields,
    ) -> Author | None:
        with self._session_factory() as session:
            author = session.get(Author, author_id)

            if author is None:
                return None

            for key, value in fields.items():
                setattr(author, key, value)

            session.commit()
            session.refresh(author)
            return author

    def delete(self, author_id: str) -> bool:
        with self._session_factory() as session:
            author = session.get(Author, author_id)

            if author is None:
                return False

            session.delete(author)
            session.commit()
            return True

    def search(self, keyword: str) -> list[Author]:
        with self._session_factory() as session:
            stmt = select(Author).where(
                or_(
                    Author.name.ilike(f"%{keyword}%"),
                    Author.bio.ilike(f"%{keyword}%"),
                )
            )

            return list(session.scalars(stmt).all())