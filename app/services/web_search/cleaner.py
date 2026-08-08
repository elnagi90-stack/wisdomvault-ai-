from __future__ import annotations

import re


def clean_quote_text(text: str) -> str:
    if not text:
        return ""

    text = text.strip()

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Fix spaces that disappeared around punctuation
    text = re.sub(r"([a-zA-Z])([.!?,;:])([A-Z])", r"\1\2 \3", text)

    # Fix common missing spaces between words
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

    # Remove Goodreads quotation marks
    text = text.strip(" \t\r\n\"“”")

    # Remove leading/trailing quote characters again
    text = re.sub(r'^[\"“”]+', "", text)
    text = re.sub(r'[\"“”]+$', "", text)

    # Normalize whitespace after cleanup
    text = re.sub(r"\s+", " ", text)

    return text.strip()
