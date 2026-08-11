from __future__ import annotations

from io import BytesIO
from unittest.mock import MagicMock, patch

from PIL import Image

from app.services.ocr_service import OcrService


def _make_test_image_bytes() -> bytes:
    image = Image.new("RGB", (200, 80), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_ocr_empty_bytes_returns_empty_string() -> None:
    service = OcrService()

    assert service.extract_text(b"") == ""


def test_ocr_invalid_bytes_returns_empty_string() -> None:
    service = OcrService()

    assert service.extract_text(b"not-an-image") == ""


def test_ocr_extracts_text_from_reader() -> None:
    service = OcrService(languages=["en"])

    fake_reader = MagicMock()
    fake_reader.readtext.return_value = [
        ([[0, 0], [100, 0], [100, 30], [0, 30]], "Never stop learning", 0.98),
        ([[0, 35], [100, 35], [100, 60], [0, 60]], "Keep growing", 0.95),
    ]

    with patch.object(
        service,
        "_get_reader",
        return_value=fake_reader,
    ):
        result = service.extract_text(_make_test_image_bytes())

    assert result == "Never stop learning Keep growing"
    fake_reader.readtext.assert_called_once()


def test_ocr_ignores_empty_detected_text() -> None:
    service = OcrService(languages=["en"])

    fake_reader = MagicMock()
    fake_reader.readtext.return_value = [
        ([[0, 0], [10, 0], [10, 10], [0, 10]], "", 0.99),
        ([[0, 0], [10, 0], [10, 10], [0, 10]], "  ", 0.99),
        ([[0, 0], [10, 0], [10, 10], [0, 10]], "Wisdom", 0.91),
    ]

    with patch.object(
        service,
        "_get_reader",
        return_value=fake_reader,
    ):
        result = service.extract_text(_make_test_image_bytes())

    assert result == "Wisdom"


def test_ocr_reader_is_loaded_lazily() -> None:
    service = OcrService()

    assert service._reader is None
