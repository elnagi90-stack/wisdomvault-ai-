from __future__ import annotations

from pydantic import BaseModel


class OcrExtractResponse(BaseModel):
    text: str
    saved_image_path: str | None = None
