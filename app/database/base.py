from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import Settings


class Base(DeclarativeBase):
    pass


def create_engine_from_settings(settings: Settings):
    return create_engine(
        settings.database_url,
        echo=settings.debug,
        future=True,
    )


def init_db(engine):

    Base.metadata.create_all(bind=engine)