from pathlib import Path

from app.core.config import Settings
from app.database.base import create_engine_from_settings, init_db
from app.database.session import build_session_factory
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.knowledge_service import KnowledgeService
from app.services.search_service import SearchService


def test_search_service_finds_relevant_entries(tmp_path: Path, monkeypatch: object) -> None:
    db_path = tmp_path / "knowledge.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("DATABASE_ENGINE", "sqlite")

    settings = Settings(_env_file=None)
    engine = create_engine_from_settings(settings)
    init_db(engine)

    repository = KnowledgeRepository(session_factory=build_session_factory(engine))
    service = KnowledgeService(repository=repository)

    service.create_entry(title="Python notes", content="FastAPI and SQLAlchemy patterns")
    service.create_entry(title="Travel plan", content="Book a flight to Cairo")

    search_service = SearchService(service)
    results = search_service.search("fastapi")

    assert len(results) == 1
    assert results[0].title == "Python notes"
