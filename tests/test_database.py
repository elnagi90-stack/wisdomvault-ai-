from sqlalchemy import select

from app.core.config import Settings
from app.database.base import Base, create_engine_from_settings
from app.database.session import build_session_factory, init_db
from app.models import KnowledgeEntry


def test_database_initializes_and_persists_entries(tmp_path: object, monkeypatch: object) -> None:
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("DATABASE_ENGINE", "sqlite")
    monkeypatch.setenv("DB_ECHO", "false")

    settings = Settings(_env_file=None)
    engine = create_engine_from_settings(settings)
    Base.metadata.drop_all(engine)

    init_db(engine)

    session_factory = build_session_factory(engine)
    with session_factory() as session:
        entry = KnowledgeEntry(title="Hello", content="World")
        session.add(entry)
        session.commit()
        saved = session.scalar(select(KnowledgeEntry))

    assert saved is not None
    assert saved.title == "Hello"
    assert saved.content == "World"
