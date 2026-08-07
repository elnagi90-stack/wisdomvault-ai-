from __future__ import annotations

import random
from typing import Protocol

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.quote import Quote
from app.models.tag import Tag


class SupportsSession(Protocol):
    def __call__(self) -> Session:
        ...


class QuoteRepository:
    def __init__(self, session_factory: SupportsSession):
        self._session_factory = session_factory

    def create(self, quote: Quote) -> Quote:
        with self._session_factory() as session:
            session.add(quote)
            session.commit()
            session.refresh(quote)
            return quote

    def get_by_id(self, quote_id: str) -> Quote | None:
        with self._session_factory() as session:
            stmt = (
                select(Quote)
                .options(
                    joinedload(Quote.book),
                    joinedload(Quote.tags),
                )
                .where(Quote.id == quote_id)
            )

            return session.scalar(stmt)

    def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Quote]:

        with self._session_factory() as session:
            stmt = (
                select(Quote)
                .options(
                    joinedload(Quote.book),
                    joinedload(Quote.tags),
                )
                .order_by(Quote.created_at.desc())
                .limit(limit)
                .offset(offset)
            )

            return list(session.scalars(stmt).unique().all())

    def search_text(
        self,
        keyword: str,
        limit: int = 50,
    ) -> list[Quote]:

        with self._session_factory() as session:
            stmt = (
                select(Quote)
                .where(Quote.text.ilike(f"%{keyword}%"))
                .options(
                    joinedload(Quote.book),
                    joinedload(Quote.tags),
                )
                .limit(limit)
            )

            return list(session.scalars(stmt).unique().all())

    def favorites(self) -> list[Quote]:

        with self._session_factory() as session:
            stmt = (
                select(Quote)
                .where(Quote.is_favorite)
                .order_by(Quote.created_at.desc())
            )

            return list(session.scalars(stmt).all())

    def by_book(self, book_id: str) -> list[Quote]:

        with self._session_factory() as session:
            stmt = select(Quote).where(Quote.book_id == book_id)

            return list(session.scalars(stmt).all())

    def by_tag(self, tag_name: str) -> list[Quote]:

        with self._session_factory() as session:
            stmt = (
                select(Quote)
                .join(Quote.tags)
                .where(Tag.name == tag_name)
            )

            return list(session.scalars(stmt).unique().all())

    def random_quote(self) -> Quote | None:

        with self._session_factory() as session:
            total = session.scalar(
                select(func.count()).select_from(Quote)
            )

            if not total:
                return None

            random_offset = random.randint(
                0,
                max(total - 1, 0),
            )

            stmt = (
                select(Quote)
                .offset(random_offset)
                .limit(1)
            )

            return session.scalar(stmt)

    def set_favorite(self, quote_id: str, is_favorite: bool) -> Quote | None:

        with self._session_factory() as session:
            quote = session.get(Quote, quote_id)

            if quote is None:
                return None

            quote.is_favorite = is_favorite
            session.commit()
            session.refresh(quote)

            return quote

    def update(self, quote_id: str, **fields) -> Quote | None:

        with self._session_factory() as session:
            quote = session.get(Quote, quote_id)

            if quote is None:
                return None

            for key, value in fields.items():
                setattr(quote, key, value)

            session.commit()
            session.refresh(quote)

            return quote

    def delete(self, quote_id: str) -> bool:

        with self._session_factory() as session:
            quote = session.get(Quote, quote_id)

            if quote is None:
                return False

            session.delete(quote)
            session.commit()

            return True

    def get_many_by_ids(
        self,
        ids: list[str],
    ) -> list[Quote]:

        with self._session_factory() as session:
            stmt = select(Quote).where(
                Quote.id.in_(ids)
            )

            return list(session.scalars(stmt).all())
