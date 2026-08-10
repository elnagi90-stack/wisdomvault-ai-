from __future__ import annotations

import re


class QuoteValidator:
    """
    Validates candidate text before semantic ranking.

    The validator is intentionally conservative:
    search-engine snippets, truncated fragments, broken sentence
    fragments, and quote-attribution remnants should not be treated
    as verified quote candidates.
    """

    MIN_WORDS = 4
    MAX_WORDS = 120

    _TRUNCATION_MARKERS = (
        "...",
        "…",
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

    _BROKEN_ENDS = (
        ",",
        ":",
        ";",
        "-",
        "―",
        "—",
    )

    _ATTRIBUTION_ENDINGS = (
        "―",
        "—",
        "--",
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

        # Reject obvious truncation.
        if any(
            marker in cleaned
            for marker in self._TRUNCATION_MARKERS
        ):
            return False

        lowered = cleaned.lower()

        # Reject fragments beginning with a dangling contraction.
        if lowered.startswith(self._BROKEN_STARTS):
            return False

        first_word = words[0].lower()

        if first_word in {
            "re",
            "s",
            "t",
            "ve",
            "ll",
            "d",
            "m",
        }:
            return False

        # Reject fragments ending in punctuation that strongly suggests
        # the sentence continues.
        if cleaned.endswith(self._BROKEN_ENDS):
            return False

        # Goodreads and similar quote pages may append an attribution
        # separator after the closing quotation mark:
        #
        #     ...never stop growing.” ―
        #
        # This is not part of the quote itself.
        if re.search(
            r"""["'”’]\s*(?:―|—|--)\s*$""",
            cleaned,
        ):
            return False

        # A dangling em dash / attribution separator is invalid even
        # without a closing quote.
        if re.search(
            r"(?:^|\s)(?:―|—|--)\s*$",
            cleaned,
        ):
            return False

        return True
