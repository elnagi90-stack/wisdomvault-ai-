from __future__ import annotations

import re
import string

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "on", "at", "for", "and", "or", "but", "that",
    "this", "it", "its", "as", "by", "with", "from", "i", "you", "he",
    "she", "we", "they", "them", "his", "her", "their", "our", "your",
    "so", "if", "than", "then", "there", "here",
}

MAX_QUERIES = 6
MAX_QUERY_WORDS = 12
KEY_PHRASE_WORDS = 4


class QueryGenerator:
    """
    Deterministic query expansion for web quote search.

    Turns one user-provided quote into a handful of distinct search
    queries — the exact phrase, and a couple of shorter "content word"
    phrases pulled from the start/end of the quote — so the search
    layer isn't limited to an exact-phrase match. No LLM/API call is
    involved; this is pure text processing and is safe to call on
    every search.
    """

    def generate(self, quote: str) -> list[str]:
        normalized = self._normalize(quote)

        if not normalized:
            return []

        queries: list[str] = [f'"{normalized}" quote']

        content_words = self._content_words(normalized)

        if len(content_words) >= 2:
            end_phrase = " ".join(content_words[-KEY_PHRASE_WORDS:])
            start_phrase = " ".join(content_words[:KEY_PHRASE_WORDS])

            queries.append(f'"{end_phrase}" quote')

            if start_phrase.lower() != end_phrase.lower():
                queries.append(f'"{start_phrase}" quote')

            queries.append(f'"{end_phrase}" wisdom')

        return self._finalize(queries)

    def _normalize(self, quote: str) -> str:
        collapsed = " ".join(quote.split()).strip()
        return collapsed.strip(string.punctuation + " ")

    def _content_words(self, normalized: str) -> list[str]:
        words = normalized.split()

        return [
            word
            for word in words
            if word.strip(string.punctuation).lower() not in _STOPWORDS
            and word.strip(string.punctuation)
        ]

    def _finalize(self, queries: list[str]) -> list[str]:
        seen: set[str] = set()
        final: list[str] = []

        for query in queries:
            words = query.split()

            if len(words) > MAX_QUERY_WORDS:
                query = " ".join(words[:MAX_QUERY_WORDS])

            key = re.sub(r"\s+", " ", query.strip().lower())

            if not key or key in seen:
                continue

            seen.add(key)
            final.append(query.strip())

            if len(final) >= MAX_QUERIES:
                break

        return final
