from __future__ import annotations

from app.ai.embedding_service import EmbeddingService
from app.core.config import settings
from app.schemas.web_search.quote import WebQuoteResult


class WebQuoteRanker:
    """
    Rank web quotes by semantic similarity to a user-provided quote,
    with a small source-quality adjustment.

    Two concepts are kept deliberately separate:

    - semantic_similarity: raw cosine similarity from the embedding
      model. This is what the minimum-quality threshold is applied
      to, BEFORE any source bonus.
    - final score (stored on WebQuoteResult.score): semantic
      similarity + a small source-quality bonus, used only to order
      the candidates that already passed the threshold.

    This ordering matters: a low-relevance quote from a reputable
    source (e.g. Goodreads) must not be able to buy its way past the
    similarity threshold just because of its source. The bonus is
    deliberately small (<= 0.05) so among candidates that DO pass the
    threshold, it can only break near-ties, never flip a real
    semantic gap.

    Uses the same BAAI/bge-m3 embedding model as the existing
    SemanticSearchService.
    """

    SOURCE_QUALITY_BONUS: dict[str, float] = {
        "goodreads": 0.05,
        "google books": 0.05,
        "internet archive": 0.05,
        "tavily search": 0.03,
    }
    DEFAULT_SOURCE_BONUS = 0.0

    def __init__(self, min_similarity: float | None = None) -> None:
        self.embedding = EmbeddingService()
        self.min_similarity = (
            min_similarity
            if min_similarity is not None
            else settings.min_semantic_similarity
        )

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

            # Threshold is applied to the RAW semantic similarity —
            # a source bonus can never rescue a candidate that isn't
            # actually relevant.
            if semantic_similarity < self.min_similarity:
                continue

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

        if not ranked:
            return []

        ranked.sort(
            key=lambda item: (
                item.score
                if item.score is not None
                else -1.0
            ),
            reverse=True,
        )

        return ranked[:limit]
