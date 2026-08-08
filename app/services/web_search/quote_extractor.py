from __future__ import annotations

import re

from bs4 import BeautifulSoup


class QuoteExtractor:
    """
    Extract quote-like passages from text and HTML.

    This class does not perform web requests.
    It receives page content and returns candidate quotes.
    """

    _DOUBLE_QUOTE_PATTERN = re.compile(
        r'"([^"\n]+)"'
    )

    _SINGLE_QUOTE_PATTERN = re.compile(
        r"'([^'\n]+)'"
    )

    MIN_QUOTE_WORDS = 3
    MAX_QUOTE_WORDS = 80

    def extract(
        self,
        text: str,
        limit: int = 10,
    ) -> list[str]:

        text = text.strip()

        if not text or limit < 1:
            return []

        candidates: list[str] = []

        candidates.extend(
            match.group(1)
            for match in self._DOUBLE_QUOTE_PATTERN.finditer(text)
        )

        candidates.extend(
            match.group(1)
            for match in self._SINGLE_QUOTE_PATTERN.finditer(text)
        )

        return self._clean_candidates(
            candidates,
            limit=limit,
        )

    def extract_html(
        self,
        html: str,
        limit: int = 10,
    ) -> list[str]:

        html = html.strip()

        if not html or limit < 1:
            return []

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        candidates: list[str] = []

        for element in soup.select("blockquote"):
            text = element.get_text(
                " ",
                strip=True,
            )

            if text:
                candidates.append(text)

        return self._clean_candidates(
            candidates,
            limit=limit,
        )

    def _clean_candidates(
        self,
        candidates: list[str],
        limit: int,
    ) -> list[str]:

        results: list[str] = []
        seen: set[str] = set()

        for candidate in candidates:

            cleaned = " ".join(
                candidate.split()
            ).strip()

            if not cleaned:
                continue

            word_count = len(cleaned.split())

            if word_count < self.MIN_QUOTE_WORDS:
                continue

            if word_count > self.MAX_QUOTE_WORDS:
                continue

            normalized = cleaned.lower()

            if normalized in seen:
                continue

            seen.add(normalized)
            results.append(cleaned)

            if len(results) >= limit:
                break

        return results
