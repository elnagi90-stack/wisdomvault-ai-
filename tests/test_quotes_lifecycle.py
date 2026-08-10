from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.database.base import create_engine_from_settings, init_db
from app.database.session import build_session_factory, get_db


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    import app.main as main_module

    # Keep FAISS index files inside this test's own tmp dir so tests
    # never read or write the developer's real storage/ directory.
    monkeypatch.chdir(tmp_path)

    db_path = tmp_path / "quotes.db"
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


def test_create_list_and_get_quote(client: TestClient) -> None:
    create = client.post(
        "/api/v1/quotes",
        json={"text": "Knowledge is power", "language": "en"},
    )
    assert create.status_code == 201
    quote_id = create.json()["id"]

    listing = client.get("/api/v1/quotes")
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    fetched = client.get(f"/api/v1/quotes/{quote_id}")
    assert fetched.status_code == 200
    assert fetched.json()["text"] == "Knowledge is power"


def test_create_quote_rejects_empty_text(client: TestClient) -> None:
    response = client.post(
        "/api/v1/quotes",
        json={"text": "   ", "language": "en"},
    )
    assert response.status_code == 400


def test_update_quote(client: TestClient) -> None:
    create = client.post(
        "/api/v1/quotes",
        json={"text": "Original text", "language": "en"},
    )
    quote_id = create.json()["id"]

    update = client.put(
        f"/api/v1/quotes/{quote_id}",
        json={"text": "Updated text", "rating": 5},
    )
    assert update.status_code == 200
    assert update.json()["text"] == "Updated text"
    assert update.json()["rating"] == 5


def test_update_quote_rejects_empty_text(client: TestClient) -> None:
    create = client.post(
        "/api/v1/quotes",
        json={"text": "Original text", "language": "en"},
    )
    quote_id = create.json()["id"]

    update = client.put(
        f"/api/v1/quotes/{quote_id}",
        json={"text": ""},
    )
    assert update.status_code == 400


def test_update_missing_quote_returns_404(client: TestClient) -> None:
    response = client.put(
        "/api/v1/quotes/does-not-exist",
        json={"rating": 1},
    )
    assert response.status_code == 404


def test_delete_quote(client: TestClient) -> None:
    create = client.post(
        "/api/v1/quotes",
        json={"text": "To be deleted", "language": "en"},
    )
    quote_id = create.json()["id"]

    delete = client.delete(f"/api/v1/quotes/{quote_id}")
    assert delete.status_code == 200

    fetched = client.get(f"/api/v1/quotes/{quote_id}")
    assert fetched.status_code == 404


def test_get_missing_quote_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/quotes/does-not-exist")
    assert response.status_code == 404


def test_favorite_and_list_favorites(client: TestClient) -> None:
    create = client.post(
        "/api/v1/quotes",
        json={"text": "A favorite quote", "language": "en"},
    )
    quote_id = create.json()["id"]

    update = client.put(
        f"/api/v1/quotes/{quote_id}",
        json={"is_favorite": True},
    )
    assert update.status_code == 200
    assert update.json()["is_favorite"] is True

    favorites = client.get("/api/v1/quotes/favorites")
    assert favorites.status_code == 200
    assert any(q["id"] == quote_id for q in favorites.json())


def test_semantic_search_returns_ok_even_without_ai_stack(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/quotes",
        json={"text": "A quote to search for", "language": "en"},
    )

    response = client.get(
        "/api/v1/quotes/semantic-search",
        params={"query": "search"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
