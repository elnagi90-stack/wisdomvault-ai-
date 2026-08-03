from __future__ import annotations

from typing import Protocol

from app.models.knowledge_entry import KnowledgeEntry


class SearchInterface(Protocol):
    def search(self, query: str) -> list[KnowledgeEntry]: ...
