from __future__ import annotations

from app.models.knowledge_entry import KnowledgeEntry
from app.services.knowledge_service import KnowledgeService


class SearchService:
    def __init__(self, knowledge_service: KnowledgeService) -> None:
        self.knowledge_service = knowledge_service

    def search(self, query: str) -> list[KnowledgeEntry]:
        query_words = {word.lower() for word in query.split() if word}
        if not query_words:
            return []

        entries = self.knowledge_service.list_entries()
        matches: list[KnowledgeEntry] = []

        for entry in entries:
            haystack = f"{entry.title} {entry.content}".lower()
            if any(word in haystack for word in query_words):
                matches.append(entry)

        return matches
