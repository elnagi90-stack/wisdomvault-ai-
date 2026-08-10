from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.database.base import Base, create_engine_from_settings


def build_session_factory(engine: Engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db(engine: Engine | None = None) -> None:
    target_engine = engine or create_engine_from_settings(Settings())
    Base.metadata.create_all(bind=target_engine)


def get_db() -> Generator[Session]:
    session_factory = build_session_factory(create_engine_from_settings(Settings()))
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
