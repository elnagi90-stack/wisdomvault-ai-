from __future__ import annotations

import re

from bs4 import BeautifulSoup


class QuoteExtractor:
    """
    Extract quote-like passages from already-fetched page content.

    This extractor does not perform network requests.
    """

    MIN_QUOTE_WORDS = 3
    MAX_QUOTE_WORDS = 80

    _DOUBLE_QUOTE_PATTERNS = (
        re.compile(r'"([^"\n]{10,})"'),
        re.compile(r"\u201c([^\u201d\n]{10,})\u201d"),
    )

    _SINGLE_QUOTE_PATTERNS = (
        re.compile(r"'([^'\n]{10,})'"),
        re.compile(r"\u2018([^\u2019\n]{10,})\u2019"),
    )

    _TRUNCATION_MARKERS = (
        "...",
        "\u2026",
    )

    def extract(
        self,
        text: str,
        limit: int = 10,
    ) -> list[str]:
        text = text.strip()

        if not text or limit < 1:
            return []

        candidates: list[str] = []

        for pattern in (
            *self._DOUBLE_QUOTE_PATTERNS,
            *self._SINGLE_QUOTE_PATTERNS,
        ):
            candidates.extend(
                match.group(1)
                for match in pattern.finditer(text)
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

        for element in soup.select("blockquote, q"):
            text = element.get_text(
                " ",
                strip=True,
            )

            if text:
                candidates.append(text)

        visible_text = soup.get_text(
            " ",
            strip=True,
        )

        candidates.extend(
            self.extract(
                visible_text,
                limit=limit,
            )
        )

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

            if any(
                marker in cleaned
                for marker in self._TRUNCATION_MARKERS
            ):
                continue

            if self._looks_like_navigation(cleaned):
                continue

            normalized = cleaned.lower()

            if normalized in seen:
                continue

            seen.add(normalized)
            results.append(cleaned)

            if len(results) >= limit:
                break

        return results

    @staticmethod
    def _looks_like_navigation(text: str) -> bool:
        lowered = text.lower()

        bad_starts = (
            "click here",
            "read more",
            "sign up",
            "log in",
            "subscribe",
        )

        return lowered.startswith(bad_starts)
