from __future__ import annotations

import io

from app.interfaces.ocr_interface import OcrInterface


class OcrEngineUnavailableError(Exception):
    """Raised when the OCR engine could not be loaded."""


class EasyOcrEngine:
    """EasyOCR-backed implementation of OcrInterface."""

    def __init__(
        self,
        languages: list[str] | None = None,
        gpu: bool = False,
    ) -> None:
        self.languages = languages or ["en", "ar"]
        self.gpu = gpu

        # Lazy-loaded per engine instance.
        self._reader = None
        self._reader_unavailable_error: Exception | None = None

    def _get_reader(self):
        if self._reader_unavailable_error is not None:
            raise OcrEngineUnavailableError(
                "EasyOCR could not be loaded."
            ) from self._reader_unavailable_error

        if self._reader is None:
            try:
                import easyocr

                self._reader = easyocr.Reader(
                    self.languages,
                    gpu=self.gpu,
                )
            except Exception as exc:  # pragma: no cover - environment-dependent
                self._reader_unavailable_error = exc
                raise OcrEngineUnavailableError(
                    "EasyOCR could not be loaded. Is it installed "
                    "(pip install easyocr)?"
                ) from exc

        return self._reader

    def extract_text(self, image_bytes: bytes) -> str:
        reader = self._get_reader()

        results = reader.readtext(
            io.BytesIO(image_bytes).getvalue(),
            detail=0,
            paragraph=True,
        )

        return "\n".join(results).strip()
