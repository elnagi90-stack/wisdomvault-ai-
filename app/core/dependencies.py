from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.session import get_db

from app.models.user import User

from app.repositories.author_repository import AuthorRepository
from app.repositories.book_repository import BookRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.repositories.quote_repository import QuoteRepository
from app.repositories.tag_repository import TagRepository
from app.repositories.user_repository import UserRepository

from app.services.author_service import AuthorService
from app.services.book_service import BookService
from app.services.category_service import CategoryService
from app.services.knowledge_service import KnowledgeService
from app.services.quote_service import QuoteService
from app.services.tag_service import TagService
from app.services.user_service import UserService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


async def get_app_context() -> dict[str, str]:
    return {"status": "ok"}


def get_author_service(session: Session = Depends(get_db)) -> AuthorService:
    return AuthorService(
        repository=AuthorRepository(session_factory=lambda: session)
    )


def get_book_service(session: Session = Depends(get_db)) -> BookService:
    return BookService(
        repository=BookRepository(session_factory=lambda: session)
    )


def get_category_service(session: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(
        repository=CategoryRepository(session_factory=lambda: session)
    )


def get_quote_service(session: Session = Depends(get_db)) -> QuoteService:
    return QuoteService(
        repository=QuoteRepository(session_factory=lambda: session)
    )


def get_tag_service(session: Session = Depends(get_db)) -> TagService:
    return TagService(
        repository=TagRepository(session_factory=lambda: session)
    )


def get_knowledge_service(session: Session = Depends(get_db)) -> KnowledgeService:
    return KnowledgeService(
        repository=KnowledgeRepository(session_factory=lambda: session)
    )


def get_user_service(session: Session = Depends(get_db)) -> UserService:
    return UserService(
        repository=UserRepository(session_factory=lambda: session)
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user = session.get(User, payload["sub"])

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


AppContext = Annotated[
    dict[str, str],
    Depends(get_app_context),
]
