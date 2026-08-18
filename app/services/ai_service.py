from __future__ import annotations

import re

import numpy as np

_MIN_SENTENCE_WORDS = 3

_SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?\u061F\u06D4])\s+")


def _split_sentences(text: str) -> list[str]:
    text = " ".join(text.split()).strip()

    if not text:
        return []

    raw_sentences = _SENTENCE_SPLIT_PATTERN.split(text)

    return [
        sentence.strip()
        for sentence in raw_sentences
        if len(sentence.split()) >= _MIN_SENTENCE_WORDS
    ]


class AiService:
    """
    Free, fully local AI helper.

    summarize() uses extractive summarization (LexRank-style centrality
    over sentence embeddings) powered by the same local, no-API-key
    embedding model already used for semantic search (BAAI/bge-m3 via
    EmbeddingService) -- no external AI API, no network call, no cost.

    If the embedding model isn't available for any reason, this falls
    back to a simple "first N sentences" summary rather than failing,
    matching the resilient-degradation pattern used elsewhere in the
    project (quote embeddings, OCR, Tavily search).
    """

    def summarize(
        self,
        text: str,
        max_sentences: int = 3,
    ) -> str:
        sentences = _split_sentences(text)

        if not sentences:
            return "Summary: (no content to summarize)"

        if len(sentences) <= max_sentences:
            return "Summary: " + " ".join(sentences)

        selected = self._select_central_sentences(sentences, max_sentences)

        return "Summary: " + " ".join(selected)

    def select_representative(
        self,
        passages: list[str],
        max_passages: int = 5,
    ) -> list[str]:
        """Picks the most representative passages from a list of
        already-discrete text units (e.g. a user's saved quotes from
        one book), using the same local centrality scoring as
        summarize() -- but without sentence-splitting, since each
        passage is already a complete unit and shouldn't be merged
        or split.

        Returns the selected passages in their original input order.
        """
        cleaned = [p.strip() for p in passages if p and p.strip()]

        if not cleaned:
            return []

        if len(cleaned) <= max_passages:
            return cleaned

        return self._select_central_sentences(cleaned, max_passages)

    def _select_central_sentences(
        self,
        sentences: list[str],
        max_sentences: int,
    ) -> list[str]:
        scores = self._centrality_scores(sentences)

        if scores is None:
            return sentences[:max_sentences]

        ranked_indices = sorted(
            range(len(sentences)),
            key=lambda i: scores[i],
            reverse=True,
        )[:max_sentences]

        for_output = sorted(ranked_indices)

        return [sentences[i] for i in for_output]

    def _centrality_scores(self, sentences: list[str]) -> np.ndarray | None:
        try:
            from app.ai.embedding_service import EmbeddingService

            vectors = EmbeddingService().encode_many(sentences)
        except Exception:
            return None

        try:
            similarity_matrix = vectors @ vectors.T
            return similarity_matrix.mean(axis=1)
        except Exception:
            return None
