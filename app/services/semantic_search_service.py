from __future__ import annotations

import json

import faiss
import numpy as np

from app.ai.embedding_service import EmbeddingService
from app.repositories.quote_repository import QuoteRepository


class SemanticSearchService:
    def __init__(
        self,
        repository: QuoteRepository,
    ) -> None:
        self.repository = repository
        self.embedding_service = EmbeddingService()

    def search(
        self,
        query: str,
        top_k: int = 5,
    ):
        quotes = self.repository.list_all(limit=100000)

        if not quotes:
            return []

        vectors = []
        valid_quotes = []

        for quote in quotes:
            if quote.embedding:
                vectors.append(json.loads(quote.embedding))
                valid_quotes.append(quote)

        if not vectors:
            return []

        matrix = np.array(
            vectors,
            dtype="float32",
        )

        index = faiss.IndexFlatIP(
            matrix.shape[1],
        )

        index.add(matrix)

        query_vector = self.embedding_service.encode_one(query)

        query_vector = np.array(
            [query_vector],
            dtype="float32",
        )

        _, indices = index.search(
            query_vector,
            min(top_k, len(valid_quotes)),
        )

        results = []

        for idx in indices[0]:
            if idx != -1:
                results.append(valid_quotes[idx])

        return results
