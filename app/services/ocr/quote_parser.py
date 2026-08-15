from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ParsedQuote:
    quote: str
    author: str | None = None
    source: str | None = None


class OcrQuoteParser:
    """
    Separates quote text from common author/source suffixes.

    Conservative by design:
    if the suffix cannot be identified reliably, it remains part
    of the quote instead of inventing metadata.
    """

    def parse(self, text: str) -> ParsedQuote:
        text = " ".join(text.split()).strip()

        if not text:
            return ParsedQuote(quote="")

        # Example:
        # quote » Marcus Aurelius Four Minute Books
        match = re.match(
            r"^(?P<quote>.+?)\s*[»\"]\s*"
            r"(?P<author>[A-Z][A-Za-z .'-]{2,60}?)"
            r"(?:\s+(?P<source>Four Minute Books))?$",
            text,
            flags=re.IGNORECASE,
        )

        if match:
            quote = match.group("quote").strip()
            author = match.group("author").strip()
            source = match.group("source")

            return ParsedQuote(
                quote=quote,
                author=author,
                source=source.strip() if source else None,
            )

        # Fallback for already-cleaned text containing
        # the known source name.
        source_match = re.search(
            r"\bFour Minute Books\b",
            text,
            flags=re.IGNORECASE,
        )

        if source_match:
            before_source = text[:source_match.start()].strip()

            # Try to identify a trailing author after the quote.
            author_match = re.search(
                r"(?P<quote>.+?)\s+"
                r"(?P<author>[A-Z][A-Za-z .'-]{2,60})$",
                before_source,
            )

            if author_match:
                return ParsedQuote(
                    quote=author_match.group("quote").strip(),
                    author=author_match.group("author").strip(),
                    source="Four Minute Books",
                )

        return ParsedQuote(quote=text)
