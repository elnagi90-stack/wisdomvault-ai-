from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.authors import router as authors_router
from app.api.v1.books import router as books_router
from app.api.v1.categories import router as categories_router
from app.api.v1.quotes import router as quotes_router
from app.api.v1.tags import router as tags_router

api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(authors_router)
api_router.include_router(books_router)
api_router.include_router(categories_router)
api_router.include_router(quotes_router)
api_router.include_router(tags_router)
