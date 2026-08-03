from __future__ import annotations

from app.models.knowledge_entry import KnowledgeEntry
from app.repositories.knowledge_repository import KnowledgeRepository, SupportsSession


class KnowledgeService:
    def __init__(self, repository: KnowledgeRepository | None = None, session_factory: SupportsSession | None = None) -> None:
        if repository is not None:
            self.repository = repository
        elif session_factory is not None:
            self.repository = KnowledgeRepository(session_factory=session_factory)
        else:
            raise TypeError("Either repository or session_factory must be provided")

    def create_entry(self, title: str, content: str) -> KnowledgeEntry:
        return self.repository.create(title=title, content=content)

    def list_entries(self) -> list[KnowledgeEntry]:
        return self.repository.list_all()
