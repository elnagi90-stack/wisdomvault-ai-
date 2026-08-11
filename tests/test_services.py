from pathlib import Path

from app.core.config import Settings
from app.database.base import create_engine_from_settings, init_db
from app.database.session import build_session_factory
from app.services.ai_service import AiService
from app.services.knowledge_service import KnowledgeService
from app.services.ocr_service import OcrService
from app.services.storage_service import LocalStorageService


def test_storage_and_knowledge_services_work(
    tmp_path: Path, monkeypatch: object
) -> None:
    db_path = tmp_path / "knowledge.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("DATABASE_ENGINE", "sqlite")

    settings = Settings(_env_file=None)
    engine = create_engine_from_settings(settings)
    init_db(engine)
    session_factory = build_session_factory(engine)
    service = KnowledgeService(session_factory=session_factory)

    entry = service.create_entry(title="Note", content="Content")
    entries = service.list_entries()

    assert entry.title == "Note"
    assert len(entries) == 1

    storage = LocalStorageService(base_path=tmp_path / "uploads")
    saved_path = storage.save_bytes("note.txt", b"hello")
    assert saved_path.exists()
    assert storage.read_text("note.txt") == "hello"

    ai_service = AiService()
    summary = ai_service.summarize(
        "This is a long document about memory and learning"
    )
    assert "Summary" in summary

    ocr_service = OcrService()
    text = ocr_service.extract_text(b"fake-image-bytes")

    # Invalid image bytes should fail gracefully.
    assert text == ""
