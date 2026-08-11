from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.dependencies import get_ocr_service
from app.database.base import create_engine_from_settings, init_db
from app.database.session import build_session_factory, get_db
from app.services.ocr_service import OcrService, UnsupportedImageError


@pytest.fixture
def fake_engine():
    engine = MagicMock()
    engine.extract_text.return_value = (
        "The important thing is to never stop learning"
    )
    return engine


@pytest.fixture
def fake_web_search_service():
    from app.schemas.web_search.quote import WebQuoteResult

    service = MagicMock()
    service.search.return_value = [
        WebQuoteResult(
            text="Live as if you were to die tomorrow. Learn as if "
            "you were to live forever.",
            author="Mahatma Gandhi",
            source="Goodreads",
            score=0.81,
        )
    ]
    return service


@pytest.fixture
def client(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fake_engine,
    fake_web_search_service,
):
    import app.main as main_module
    from app.api.v1.web_search import get_web_search_service

    monkeypatch.chdir(tmp_path)

    db_path = tmp_path / "ocr.db"
    settings = Settings(database_url=f"sqlite:///{db_path}", _env_file=None)
    engine = create_engine_from_settings(settings)
    init_db(engine)
    session_factory = build_session_factory(engine)

    def override_get_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def override_get_ocr_service():
        return OcrService(engine=fake_engine)

    def override_get_web_search_service():
        return fake_web_search_service

    main_module.app.dependency_overrides[get_db] = override_get_db
    main_module.app.dependency_overrides[get_ocr_service] = (
        override_get_ocr_service
    )
    main_module.app.dependency_overrides[get_web_search_service] = (
        override_get_web_search_service
    )

    yield TestClient(main_module.app)

    main_module.app.dependency_overrides.pop(get_db, None)
    main_module.app.dependency_overrides.pop(get_ocr_service, None)
    main_module.app.dependency_overrides.pop(
        get_web_search_service, None
    )


def _auth_headers(client: TestClient) -> dict:
    client.post(
        "/api/v1/users/register",
        json={
            "username": "ocruser",
            "email": "ocruser@example.com",
            "password": "supersecret123",
        },
    )
    token = client.post(
        "/api/v1/users/login",
        data={"username": "ocruser@example.com", "password": "supersecret123"},
    ).json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def _fake_image_file() -> tuple[str, io.BytesIO, str]:
    return ("page.png", io.BytesIO(b"fake-png-bytes"), "image/png")


# ---- OcrService unit tests ----

def test_legacy_zero_arg_construction_returns_empty_for_invalid_bytes() -> None:
    service = OcrService()
    text = service.extract_text(b"fake-image-bytes")

    assert text == ""

# ---- /api/v1/ocr/extract ----

def test_extract_requires_authentication(client: TestClient) -> None:
    filename, filedata, content_type = _fake_image_file()

    response = client.post(
        "/api/v1/ocr/extract",
        files={"file": (filename, filedata, content_type)},
    )
    assert response.status_code == 401


def test_extract_returns_text_from_engine(
    client: TestClient, fake_engine
) -> None:
    headers = _auth_headers(client)
    filename, filedata, content_type = _fake_image_file()

    response = client.post(
        "/api/v1/ocr/extract",
        files={"file": (filename, filedata, content_type)},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["text"] == (
        "The important thing is to never stop learning"
    )
    fake_engine.extract_text.assert_called_once()


def test_extract_rejects_non_image_upload(client: TestClient) -> None:
    headers = _auth_headers(client)

    response = client.post(
        "/api/v1/ocr/extract",
        files={"file": ("notes.pdf", io.BytesIO(b"pdf bytes"), "application/pdf")},
        headers=headers,
    )
    assert response.status_code == 400


# ---- /api/v1/ocr/search Ã¢â‚¬â€ the actual OCR-into-discovery pipeline ----

def test_ocr_search_requires_authentication(client: TestClient) -> None:
    filename, filedata, content_type = _fake_image_file()

    response = client.post(
        "/api/v1/ocr/search",
        files={"file": (filename, filedata, content_type)},
    )
    assert response.status_code == 401


def test_ocr_search_feeds_extracted_text_into_web_search_service(
    client: TestClient, fake_engine, fake_web_search_service
) -> None:
    headers = _auth_headers(client)
    filename, filedata, content_type = _fake_image_file()

    response = client.post(
        "/api/v1/ocr/search",
        files={"file": (filename, filedata, content_type)},
        headers=headers,
    )

    assert response.status_code == 200

    fake_web_search_service.search.assert_called_once_with(
        "The important thing is to never stop learning",
        limit=5,
    )

    body = response.json()
    assert len(body) == 1
    assert body[0]["author"] == "Mahatma Gandhi"


def test_ocr_search_respects_limit_param(
    client: TestClient, fake_web_search_service
) -> None:
    headers = _auth_headers(client)
    filename, filedata, content_type = _fake_image_file()

    client.post(
        "/api/v1/ocr/search",
        files={"file": (filename, filedata, content_type)},
        params={"limit": 3},
        headers=headers,
    )

    fake_web_search_service.search.assert_called_once_with(
        "The important thing is to never stop learning",
        limit=3,
    )


def test_ocr_search_returns_422_when_no_text_extracted(
    client: TestClient, fake_engine
) -> None:
    fake_engine.extract_text.return_value = ""
    headers = _auth_headers(client)
    filename, filedata, content_type = _fake_image_file()

    response = client.post(
        "/api/v1/ocr/search",
        files={"file": (filename, filedata, content_type)},
        headers=headers,
    )
    assert response.status_code == 422
