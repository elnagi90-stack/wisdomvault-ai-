from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.knowledge_service import KnowledgeService


async def get_app_context() -> dict[str, str]:
    return {"status": "ok"}


def get_knowledge_service(session: Session = Depends(get_db)) -> KnowledgeService:
    repository = KnowledgeRepository(session_factory=lambda: session)
    return KnowledgeService(repository=repository)


AppContext = Annotated[dict[str, str], Depends(get_app_context)]
