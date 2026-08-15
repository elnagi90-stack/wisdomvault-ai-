from __future__ import annotations

import re


class OcrTextCleaner:
    """
    Cleans common OCR artifacts before sending extracted text
    to the web-search layer.
    """

    REPLACEMENTS = {
        "Miinute": "Minute",
        "Miinutes": "Minutes",
        "Bools": "Books",
        "Bool": "Book",
    }

    def clean(self, text: str) -> str:
        if not text:
            return ""

        text = text.strip()

        for wrong, correct in self.REPLACEMENTS.items():
            text = text.replace(wrong, correct)

        text = text.replace("«", "").replace("»", "")
        text = text.replace('"', "")

        text = re.sub(r"\s+", " ", text).strip()

        return text
