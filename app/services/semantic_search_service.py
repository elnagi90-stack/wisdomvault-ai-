from __future__ import annotations

import json

from app.ai.embedding_service import EmbeddingService
from app.ai.vector_store import VectorStore
from app.repositories.quote_repository import QuoteRepository


class SemanticSearchService:
    def __init__(self, repository: QuoteRepository):
        self.repository = repository
        self.vector_store = VectorStore()
        self._loaded = False

    def _build_index(self):
        if self._loaded:
            return

        quotes = self.repository.list_all()

        for quote in quotes:
            if not quote.embedding:
                continue

            vector = json.loads(quote.embedding)
            self.vector_store.add(vector, quote.id)

        self._loaded = True

    def search(self, text: str, top_k: int = 5):
        self._build_index()

        vector = EmbeddingService().encode_one(text)

        results = self.vector_store.search(
            vector,
            k=top_k,
        )

        return results
