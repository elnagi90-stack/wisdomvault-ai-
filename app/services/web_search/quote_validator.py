from __future__ import annotations

import re


class QuoteValidator:
    """
    Validates candidate text before it reaches semantic ranking.

    The validator is intentionally conservative:
    search-engine snippets and truncated fragments should not be
    treated as verified quotes.
    """

    MIN_WORDS = 4
    MAX_WORDS = 120

    _TRUNCATION_MARKERS = (
        "...",
        "?",
    )

    _BROKEN_STARTS = (
        "re ",
        "'re ",
        "s ",
        "'s ",
        "t ",
        "'t ",
        "ve ",
        "'ve ",
        "ll ",
        "'ll ",
        "d ",
        "'d ",
        "m ",
        "'m ",
    )

    def is_valid(self, text: str) -> bool:
        if not text:
            return False

        cleaned = " ".join(text.split()).strip()

        if not cleaned:
            return False

        words = cleaned.split()

        if len(words) < self.MIN_WORDS:
            return False

        if len(words) > self.MAX_WORDS:
            return False

        if any(marker in cleaned for marker in self._TRUNCATION_MARKERS):
            return False

        lowered = cleaned.lower()

        if lowered.startswith(self._BROKEN_STARTS):
            return False

        if re.match(r"^[a-zA-Z]{1,3}\s", cleaned):
            first_word = words[0].lower()
            if first_word in {"re", "s", "t", "ve", "ll", "d", "m"}:
                return False

        if cleaned.endswith((",", ":", ";", "-", "?")):
            return False

        return True
