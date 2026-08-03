from __future__ import annotations

from typing import Protocol


class AiInterface(Protocol):
    def summarize(self, text: str) -> str: ...
