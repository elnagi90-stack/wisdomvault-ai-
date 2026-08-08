from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.database.base import create_engine_from_settings, init_db
from app.database.session import build_session_factory, get_db
from app.integrations.notion.oauth import (
    create_state_token,
    verify_state_token,
)


@pytest.fixture
def notion_settings() -> Settings:
    return Settings(
        notion_client_id="test-client-id",
        notion_client_secret="test-client-secret",
        notion_redirect_uri="http://testserver/api/v1/notion/callback",
        secret_key="test-secret-key",
        _env_file=None,
    )


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, notion_settings: Settings):
    import app.main as main_module
    import app.core.config as config_module
    import app.api.v1.notion as notion_module

    monkeypatch.chdir(tmp_path)

    # Point the module-level `settings` singleton (used by security.py,
    # notion.py, etc.) at test-specific values for this test only.
    monkeypatch.setattr(config_module, "settings", notion_settings)
    monkeypatch.setattr(notion_module, "settings", notion_settings)

    db_path = tmp_path / "notion.db"
    db_settings = Settings(database_url=f"sqlite:///{db_path}", _env_file=None)
    engine = create_engine_from_settings(db_settings)
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
            "username": "notionuser",
            "email": "notionuser@example.com",
            "password": "supersecret123",
        },
    )
    token = client.post(
        "/api/v1/users/login",
        data={"username": "notionuser@example.com", "password": "supersecret123"},
    ).json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


# ---- state token unit tests (no HTTP involved) ----

def test_state_token_round_trips(notion_settings: Settings) -> None:
    token = create_state_token("user-123", notion_settings)
    assert verify_state_token(token, notion_settings) == "user-123"


def test_state_token_rejects_tampering(notion_settings: Settings) -> None:
    token = create_state_token("user-123", notion_settings)
    header, payload, signature = token.split(".")

    # Flip a character in the middle of the signature rather than the
    # very last character: base64's final character can have "don't
    # care" bits, so tampering it sometimes decodes to the same bytes
    # by coincidence and makes this test flaky.
    mid = len(signature) // 2
    flipped_char = "A" if signature[mid] != "A" else "B"
    tampered_signature = signature[:mid] + flipped_char + signature[mid + 1 :]
    tampered = f"{header}.{payload}.{tampered_signature}"

    assert verify_state_token(tampered, notion_settings) is None


def test_state_token_from_different_secret_is_rejected(
    notion_settings: Settings,
) -> None:
    token = create_state_token("user-123", notion_settings)
    other = Settings(secret_key="a-completely-different-key", _env_file=None)
    assert verify_state_token(token, other) is None


# ---- API flow tests ----

def test_connect_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/notion/connect")
    assert response.status_code == 401


def test_connect_returns_an_authorize_url(client: TestClient) -> None:
    headers = _auth_headers(client)

    response = client.get("/api/v1/notion/connect", headers=headers)
    assert response.status_code == 200

    url = response.json()["authorize_url"]
    assert url.startswith("https://api.notion.com/v1/oauth/authorize")
    assert "client_id=test-client-id" in url
    assert "state=" in url


def test_callback_rejects_invalid_state(client: TestClient) -> None:
    response = client.get(
        "/api/v1/notion/callback",
        params={"code": "abc", "state": "not-a-real-token"},
    )
    assert response.status_code == 400


def test_callback_exchanges_code_and_saves_token(
    client: TestClient, notion_settings: Settings
) -> None:
    headers = _auth_headers(client)

    me = client.get("/api/v1/users/me", headers=headers).json()
    state = create_state_token(me["id"], notion_settings)

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "access_token": "secret-notion-token",
        "workspace_id": "workspace-abc",
    }

    with patch("httpx.post", return_value=fake_response):
        response = client.get(
            "/api/v1/notion/callback",
            params={"code": "auth-code-123", "state": state},
        )

    assert response.status_code == 200
    assert response.json()["connected"] is True
    assert response.json()["workspace_id"] == "workspace-abc"

    status = client.get("/api/v1/notion/status", headers=headers)
    assert status.json()["connected"] is True
    assert status.json()["workspace_id"] == "workspace-abc"


def test_sync_fails_cleanly_when_not_connected(client: TestClient) -> None:
    headers = _auth_headers(client)

    quote = client.post(
        "/api/v1/quotes",
        json={"text": "A quote to sync", "language": "en"},
        headers=headers,
    ).json()

    response = client.post(
        f"/api/v1/notion/sync/{quote['id']}",
        headers=headers,
    )
    assert response.status_code == 400
    assert "not connected" in response.json()["detail"].lower()


def test_full_sync_creates_a_notion_page(
    client: TestClient, notion_settings: Settings
) -> None:
    headers = _auth_headers(client)

    me = client.get("/api/v1/users/me", headers=headers).json()
    state = create_state_token(me["id"], notion_settings)

    fake_token_response = MagicMock()
    fake_token_response.status_code = 200
    fake_token_response.json.return_value = {
        "access_token": "secret-notion-token",
        "workspace_id": "workspace-abc",
    }

    with patch("httpx.post", return_value=fake_token_response):
        client.get(
            "/api/v1/notion/callback",
            params={"code": "auth-code-123", "state": state},
        )

    client.post(
        "/api/v1/notion/database",
        json={"database_id": "db-123"},
        headers=headers,
    )

    quote = client.post(
        "/api/v1/quotes",
        json={"text": "A quote to sync", "language": "en"},
        headers=headers,
    ).json()

    fake_page_response = MagicMock()
    fake_page_response.status_code = 200
    fake_page_response.json.return_value = {"id": "notion-page-id-1"}

    with patch("httpx.request", return_value=fake_page_response) as mocked:
        response = client.post(
            f"/api/v1/notion/sync/{quote['id']}",
            headers=headers,
        )

    assert response.status_code == 200
    assert mocked.call_args.args[0] == "POST"
    assert mocked.call_args.args[1] == "https://api.notion.com/v1/pages"

    fetched = client.get(f"/api/v1/quotes/{quote['id']}")
    assert fetched.status_code == 200
