from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user, get_quote_service
from app.models.user import User
from app.schemas.quote import QuoteResponse
from app.schemas.web_search.quote import WebQuoteResult
from app.services.quote_service import QuoteService
from app.services.web_search.service import WebSearchService

router = APIRouter(
    prefix="/web-search",
    tags=["Web Search"],
)


def get_web_search_service() -> WebSearchService:
    return WebSearchService()


@router.get(
    "",
    response_model=list[WebQuoteResult],
)
def search_quotes_online(
    q: str,
    limit: int = 10,
    service: WebSearchService = Depends(get_web_search_service),
    current_user: User = Depends(get_current_user),
):
    if len(q.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Search query must be at least 2 characters.",
        )

    return service.search(query=q, limit=limit)


@router.post(
    "/import",
    response_model=QuoteResponse,
    status_code=201,
)
def import_quote_from_web(
    payload: WebQuoteResult,
    quote_service: QuoteService = Depends(get_quote_service),
    current_user: User = Depends(get_current_user),
):
    notes = None

    if payload.source or payload.url:
        notes = f"Imported from {payload.source or 'web'}: {payload.url or ''}".strip()

    try:
        return quote_service.create_quote(
            text=payload.text,
            notes=notes,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
