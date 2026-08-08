from __future__ import annotations

from app.ai.embedding_service import EmbeddingService
from app.schemas.web_search.quote import WebQuoteResult


class WebQuoteRanker:
    """
    Rank web quotes by semantic similarity to a user-provided quote.

    Uses the same BAAI/bge-m3 embedding model as the existing
    SemanticSearchService.
    """

    def __init__(self) -> None:
        self.embedding = EmbeddingService()

    def rank(
        self,
        query: str,
        results: list[WebQuoteResult],
        limit: int = 10,
    ) -> list[WebQuoteResult]:

        query = query.strip()

        if not query or not results or limit < 1:
            return []

        valid_results = [
            result
            for result in results
            if result.text and result.text.strip()
        ]

        if not valid_results:
            return []

        query_vector = self.embedding.encode_one(query)

        quote_vectors = self.embedding.encode_many(
            [result.text for result in valid_results]
        )

        ranked: list[WebQuoteResult] = []

        for result, quote_vector in zip(
            valid_results,
            quote_vectors,
        ):
            # Embeddings are normalized, so dot product
            # is equivalent to cosine similarity.
            score = float(query_vector @ quote_vector)

            ranked.append(
                result.model_copy(
                    update={
                        "score": round(score, 4),
                    }
                )
            )

        ranked.sort(
            key=lambda item: (
                item.score
                if item.score is not None
                else -1.0
            ),
            reverse=True,
        )

        return ranked[:limit]
