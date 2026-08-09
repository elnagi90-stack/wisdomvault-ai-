from __future__ import annotations

from app.ai.embedding_service import EmbeddingService
from app.schemas.web_search.quote import WebQuoteResult


class WebQuoteRanker:
    """
    Rank web quotes by semantic similarity to a user-provided quote,
    with a small source-quality adjustment.

    Semantic similarity stays the dominant signal (it drives the
    ordering in the overwhelming majority of cases); source quality
    only breaks near-ties between otherwise similar candidates. The
    bonus is deliberately small (<= 0.05) so it can never flip the
    ranking between a strong semantic match from a lesser-known
    source and a weak match from a reputable one.

    Uses the same BAAI/bge-m3 embedding model as the existing
    SemanticSearchService.
    """

    # Small, capped bonuses — not meant to compete with semantic
    # similarity, only to nudge otherwise-close candidates toward
    # more reliable sources.
    SOURCE_QUALITY_BONUS: dict[str, float] = {
        "goodreads": 0.05,
        "google books": 0.05,
        "internet archive": 0.05,
        "tavily search": 0.03,
    }
    DEFAULT_SOURCE_BONUS = 0.0

    def __init__(self) -> None:
        self.embedding = EmbeddingService()

    def _source_bonus(self, source: str | None) -> float:
        if not source:
            return self.DEFAULT_SOURCE_BONUS

        return self.SOURCE_QUALITY_BONUS.get(
            source.strip().lower(),
            self.DEFAULT_SOURCE_BONUS,
        )

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
            semantic_similarity = float(query_vector @ quote_vector)
            combined_score = semantic_similarity + self._source_bonus(
                result.source
            )

            ranked.append(
                result.model_copy(
                    update={
                        "score": round(combined_score, 4),
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
