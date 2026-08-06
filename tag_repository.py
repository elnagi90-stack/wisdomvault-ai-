from __future__ import annotations

from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tag import Tag


class SupportsSession(Protocol):
    def __call__(self) -> Session: ...


class TagRepository:
    def __init__(self, session_factory: SupportsSession):
        self._session_factory = session_factory

    def create(self, tag: Tag) -> Tag:
        with self._session_factory() as session:
            session.add(tag)
            session.commit()
            session.refresh(tag)
            return tag

    def get_by_id(self, tag_id: str) -> Tag | None:
        with self._session_factory() as session:
            return session.get(Tag, tag_id)

    def list_all(self) -> list[Tag]:
        with self._session_factory() as session:
            return list(session.scalars(select(Tag)).all())

    def delete(self, tag_id: str) -> bool:
        with self._session_factory() as session:
            tag = session.get(Tag, tag_id)

            if tag is None:
                return False

            session.delete(tag)
            session.commit()
            return True

    def search(self, keyword: str) -> list[Tag]:
        with self._session_factory() as session:
            stmt = select(Tag).where(Tag.name.ilike(f"%{keyword}%"))
            return list(session.scalars(stmt).all())
