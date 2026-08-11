from __future__ import annotations

import io

_reader = None
_reader_unavailable_error: Exception | None = None


class OcrEngineUnavailableError(Exception):
    """Raised when the OCR engine could not be loaded (missing deps, etc.)."""


class PlaceholderOcrEngine:
    """Default no-dependency engine used when nothing else is configured.

    Kept so the existing zero-argument OcrService() construction (and
    the Foundation-phase demo /ocr endpoint / test that rely on it)
    keeps working exactly as before.
    """

    def extract_text(self, image_bytes: bytes) -> str:
        return "placeholder OCR output from fake image bytes"


class EasyOcrEngine:
    """EasyOCR-backed implementation of OcrInterface.

    Mixed Arabic/English is the common case for this project (medical
    textbooks in English, personal notes in Arabic), so both languages
    are loaded by default.
    """

    def __init__(self, languages: list[str] | None = None, gpu: bool = False) -> None:
        self.languages = languages or ["en", "ar"]
        self.gpu = gpu

    def _get_reader(self):
        global _reader, _reader_unavailable_error

        if _reader_unavailable_error is not None:
            raise OcrEngineUnavailableError(
                "EasyOCR could not be loaded."
            ) from _reader_unavailable_error

        if _reader is None:
            try:
                import easyocr

                _reader = easyocr.Reader(self.languages, gpu=self.gpu)
            except Exception as exc:  # pragma: no cover - environment-dependent
                _reader_unavailable_error = exc
                raise OcrEngineUnavailableError(
                    "EasyOCR could not be loaded. Is it installed "
                    "(pip install easyocr)?"
                ) from exc

        return _reader

    def extract_text(self, image_bytes: bytes) -> str:
        reader = self._get_reader()

        results = reader.readtext(
            io.BytesIO(image_bytes).getvalue(),
            detail=0,
            paragraph=True,
        )

        return "\n".join(results).strip()
