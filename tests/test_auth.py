from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.database.base import create_engine_from_settings, init_db
from app.database.session import build_session_factory, get_db


@pytest.fixture
def client(tmp_path: Path):
    import app.main as main_module

    db_path = tmp_path / "auth.db"
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


def _register(client: TestClient, email: str = "user@example.com") -> dict:
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": email.split("@")[0],
            "email": email,
            "password": "supersecret123",
        },
    )
    assert response.status_code == 201
    return response.json()


def _login(client: TestClient, email: str = "user@example.com") -> str:
    response = client.post(
        "/api/v1/users/login",
        data={"username": email, "password": "supersecret123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_register_and_login_flow(client: TestClient) -> None:
    user = _register(client)
    assert user["email"] == "user@example.com"
    assert user["is_superuser"] is False

    token = _login(client)
    assert token

    me = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "user@example.com"


def test_duplicate_registration_is_rejected(client: TestClient) -> None:
    _register(client)

    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "user",
            "email": "user@example.com",
            "password": "supersecret123",
        },
    )
    assert response.status_code == 400


def test_login_with_wrong_password_fails(client: TestClient) -> None:
    _register(client)

    response = client.post(
        "/api/v1/users/login",
        data={"username": "user@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_me_requires_a_valid_token(client: TestClient) -> None:
    no_token = client.get("/api/v1/users/me")
    assert no_token.status_code == 401

    bad_token = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert bad_token.status_code == 401


def test_list_users_requires_admin(client: TestClient) -> None:
    _register(client)
    token = _login(client)

    no_auth = client.get("/api/v1/users")
    assert no_auth.status_code == 401

    as_regular_user = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert as_regular_user.status_code == 403
