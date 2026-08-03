from __future__ import annotations


class AiService:
    def summarize(self, text: str) -> str:
        return f"Summary: {text[:80]}"
