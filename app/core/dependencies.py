from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.author_repository import AuthorRepository
from app.repositories.book_repository import BookRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.repositories.quote_repository import QuoteRepository
from app.repositories.tag_repository import TagRepository
from app.services.author_service import AuthorService
from app.services.book_service import BookService
from app.services.knowledge_service import KnowledgeService
from app.services.quote_service import QuoteService
from app.services.tag_service import TagService


async def get_app_context() -> dict[str, str]:
    return {"status": "ok"}


def get_knowledge_service(
    session: Session = Depends(get_db),
) -> KnowledgeService:
    repository = KnowledgeRepository(
        session_factory=lambda: session,
    )

    return KnowledgeService(
        repository=repository,
    )


def get_quote_service(
    session: Session = Depends(get_db),
) -> QuoteService:
    repository = QuoteRepository(
        session_factory=lambda: session,
    )

    return QuoteService(
        repository=repository,
    )


def get_author_service(
    session: Session = Depends(get_db),
) -> AuthorService:
    repository = AuthorRepository(
        session_factory=lambda: session,
    )
    return AuthorService(
        repository=repository,
    )


def get_book_service(
    session: Session = Depends(get_db),
) -> BookService:
    repository = BookRepository(
        session_factory=lambda: session,
    )
    return BookService(
        repository=repository,
    )


def get_tag_service(
    session: Session = Depends(get_db),
) -> TagService:
    repository = TagRepository(
        session_factory=lambda: session,
    )
    return TagService(
        repository=repository,
    )


AppContext = Annotated[
    dict[str, str],
    Depends(get_app_context),
]
