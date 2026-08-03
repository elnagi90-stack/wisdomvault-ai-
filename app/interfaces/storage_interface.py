from __future__ import annotations

from pathlib import Path
from typing import Protocol


class StorageInterface(Protocol):
    def save_bytes(self, filename: str, content: bytes) -> Path: ...

    def read_text(self, filename: str) -> str: ...
