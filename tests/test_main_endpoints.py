from fastapi.testclient import TestClient

import app.main as main_module


def test_main_endpoints_are_available() -> None:
    client = TestClient(main_module.app)

    root = client.get("/")
    assert root.status_code == 200

    health = client.get("/health")
    assert health.status_code == 200

    create = client.post("/knowledge?title=Hello&content=World")
    assert create.status_code == 200

    entries = client.get("/knowledge")
    assert entries.status_code == 200

    upload = client.post("/upload?filename=test.txt&content=hello")
    assert upload.status_code == 200

    summary = client.get("/summary?text=hello")
    assert summary.status_code == 200

    ocr = client.get("/ocr")
    assert ocr.status_code == 200


def test_write_endpoints_require_api_key(monkeypatch: object) -> None:
    monkeypatch.setattr(main_module.settings, "api_key", "secret")
    client = TestClient(main_module.app)

    response = client.post("/knowledge?title=Hello&content=World")
    assert response.status_code == 401

    authorized = client.post(
        "/knowledge?title=Hello&content=World",
        headers={"X-API-KEY": "secret"},
    )
    assert authorized.status_code == 200
