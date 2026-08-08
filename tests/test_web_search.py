from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.database.base import create_engine_from_settings, init_db
from app.database.session import build_session_factory, get_db
from app.schemas.web_search.quote import WebQuoteResult


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    import app.main as main_module

    monkeypatch.chdir(tmp_path)

    db_path = tmp_path / "web_search.db"
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

    main_module.app.dependency_overrides[get_db] = override_get_db

    yield TestClient(main_module.app)

    main_module.app.dependency_overrides.pop(get_db, None)


def _auth_headers(client: TestClient) -> dict:
    client.post(
        "/api/v1/users/register",
        json={
            "username": "searcher",
            "email": "searcher@example.com",
            "password": "supersecret123",
        },
    )
    token = client.post(
        "/api/v1/users/login",
        data={"username": "searcher@example.com", "password": "supersecret123"},
    ).json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_search_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/web-search", params={"q": "wisdom"})
    assert response.status_code == 401


def test_search_rejects_short_queries(client: TestClient) -> None:
    headers = _auth_headers(client)

    response = client.get(
        "/api/v1/web-search",
        params={"q": "a"},
        headers=headers,
    )
    assert response.status_code == 400


def test_search_returns_results(client: TestClient) -> None:
    headers = _auth_headers(client)

    fake_results = [
        WebQuoteResult(
            text="Knowledge speaks, wisdom listens",
            author="Jimi Hendrix",
            source="Goodreads",
            url="https://goodreads.com/x",
        )
    ]

    with patch(
        "app.services.web_search.service.WebSearchService.search",
        return_value=fake_results,
    ):
        response = client.get(
            "/api/v1/web-search",
            params={"q": "wisdom"},
            headers=headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["text"] == "Knowledge speaks, wisdom listens"


def test_import_creates_a_real_quote(client: TestClient) -> None:
    headers = _auth_headers(client)

    response = client.post(
        "/api/v1/web-search/import",
        json={
            "text": "Knowledge speaks, wisdom listens",
            "author": "Jimi Hendrix",
            "source": "Goodreads",
            "url": "https://goodreads.com/x",
        },
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["text"] == "Knowledge speaks, wisdom listens"
    assert "Goodreads" in response.json()["notes"]

    listing = client.get("/api/v1/quotes")
    assert len(listing.json()) == 1


def test_import_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/api/v1/web-search/import",
        json={"text": "Some quote"},
    )
    assert response.status_code == 401
