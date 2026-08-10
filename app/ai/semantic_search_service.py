from __future__ import annotations

from app.ai.embedding_service import EmbeddingService
from app.repositories.quote_repository import QuoteRepository
from app.vector.faiss_manager import FaissManager


class SemanticSearchService:
    def __init__(
        self,
        repository: QuoteRepository,
    ):
        self.repository = repository
        self.embedding = EmbeddingService()
        self.index = FaissManager()

    def search(
        self,
        query: str,
        k: int = 5,
    ):
        vector = self.embedding.encode_one(query)

        matches = self.index.search(
            vector,
            k=k,
        )

        if not matches:
            return []

        ids = [quote_id for quote_id, _ in matches]

        quotes = self.repository.get_many_by_ids(ids)

        quotes_map = {
            quote.id: quote
            for quote in quotes
        }

        results = []

        for quote_id, score in matches:
            quote = quotes_map.get(quote_id)

            if quote is None:
                continue

            results.append(
                {
                    "score": round(score, 4),
                    "quote": quote,
                }
            )

        return results
