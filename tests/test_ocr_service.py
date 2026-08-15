from __future__ import annotations

from io import BytesIO
from unittest.mock import MagicMock

from PIL import Image

from app.services.ocr_service import OcrService


def _make_test_image_bytes() -> bytes:
    image = Image.new("RGB", (200, 80), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_ocr_empty_bytes_returns_empty_string() -> None:
    engine = MagicMock()
    service = OcrService(engine=engine)

    assert service.extract_text(b"") == ""
    engine.extract_text.assert_not_called()


def test_ocr_invalid_bytes_returns_empty_string() -> None:
    engine = MagicMock()
    service = OcrService(engine=engine)

    # extract_text() delegates to the injected engine.
    engine.extract_text.return_value = "ignored by this test"

    result = service.extract_text(b"not-an-image")

    assert result == "ignored by this test"
    engine.extract_text.assert_called_once_with(b"not-an-image")


def test_ocr_extracts_text_from_engine() -> None:
    engine = MagicMock()
    engine.extract_text.return_value = (
        "Never stop learning Keep growing"
    )

    service = OcrService(
        engine=engine,
        languages=["en"],
    )

    result = service.extract_text(_make_test_image_bytes())

    assert result == "Never stop learning Keep growing"
    engine.extract_text.assert_called_once()


def test_ocr_strips_engine_result() -> None:
    engine = MagicMock()
    engine.extract_text.return_value = "  Wisdom  "

    service = OcrService(engine=engine)

    result = service.extract_text(_make_test_image_bytes())

    assert result == "Wisdom"


def test_ocr_engine_failure_returns_empty_string() -> None:
    engine = MagicMock()
    engine.extract_text.side_effect = RuntimeError("OCR failed")

    service = OcrService(engine=engine)

    result = service.extract_text(_make_test_image_bytes())

    assert result == ""
    engine.extract_text.assert_called_once()
