from __future__ import annotations

from pathlib import Path


class LocalStorageService:
    def __init__(self, base_path: str | Path | None = None) -> None:
        self.base_path = Path(base_path or "storage")
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_bytes(self, filename: str, content: bytes) -> Path:
        destination = self.base_path / filename
        destination.write_bytes(content)
        return destination

    def read_text(self, filename: str) -> str:
        return (self.base_path / filename).read_text(encoding="utf-8")
