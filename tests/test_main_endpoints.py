from fastapi.testclient import TestClient

from app.main import app


def test_main_endpoints_are_available() -> None:
    client = TestClient(app)

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
