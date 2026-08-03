from __future__ import annotations

from typing import Protocol

from sqlalchemy.orm import Session

from app.models.knowledge_entry import KnowledgeEntry


class SupportsSession(Protocol):
    def __call__(self) -> Session: ...


class KnowledgeRepository:
    def __init__(self, session_factory: SupportsSession) -> None:
        self._session_factory = session_factory

    def create(self, title: str, content: str) -> KnowledgeEntry:
        with self._session_factory() as session:
            entry = KnowledgeEntry(title=title, content=content)
            session.add(entry)
            session.commit()
            session.refresh(entry)
            return entry

    def list_all(self) -> list[KnowledgeEntry]:
        with self._session_factory() as session:
            return list(session.query(KnowledgeEntry).all())
