from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_quote_service
from app.schemas.quote import QuoteCreate, QuoteResponse
from app.services.quote_service import QuoteService
from app.services.semantic_search_service import SemanticSearchService

router = APIRouter(
    prefix="/quotes",
    tags=["Quotes"],
)


@router.get(
    "",
    response_model=list[QuoteResponse],
)
def list_quotes(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: QuoteService = Depends(get_quote_service),
):
    return service.list_quotes(
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=QuoteResponse,
)
def create_quote(
    payload: QuoteCreate,
    service: QuoteService = Depends(get_quote_service),
):
    return service.create_quote(
        text=payload.text,
        book_id=payload.book_id,
        page_number=payload.page_number,
        chapter=payload.chapter,
        language=payload.language,
        notes=payload.notes,
        rating=payload.rating,
        is_favorite=payload.is_favorite,
    )


@router.get(
    "/random",
    response_model=QuoteResponse,
)
def random_quote(
    service: QuoteService = Depends(get_quote_service),
):
    quote = service.get_random_quote()

    if quote is None:
        raise HTTPException(
            status_code=404,
            detail="No quotes found",
        )

    return quote


@router.get(
    "/favorites",
    response_model=list[QuoteResponse],
)
def favorite_quotes(
    service: QuoteService = Depends(get_quote_service),
):
    return service.get_favorites()


@router.get(
    "/book/{book_id}",
    response_model=list[QuoteResponse],
)
def quotes_by_book(
    book_id: str,
    service: QuoteService = Depends(get_quote_service),
):
    return service.get_quotes_by_book(book_id)


@router.get(
    "/tag/{tag_name}",
    response_model=list[QuoteResponse],
)
def quotes_by_tag(
    tag_name: str,
    service: QuoteService = Depends(get_quote_service),
):
    return service.get_quotes_by_tag(tag_name)


@router.get(
    "/search",
    response_model=list[QuoteResponse],
)
def search_quotes(
    keyword: str,
    limit: int = Query(default=50, ge=1, le=100),
    service: QuoteService = Depends(get_quote_service),
):
    return service.search_quotes(
        keyword=keyword,
        limit=limit,
    )


@router.get(
    "/{quote_id}",
    response_model=QuoteResponse,
)
def get_quote(
    quote_id: str,
    service: QuoteService = Depends(get_quote_service),
):
    quote = service.get_quote(quote_id)

    if quote is None:
        raise HTTPException(
            status_code=404,
            detail="Quote not found",
        )

    return quote


@router.delete(
    "/{quote_id}",
)
def delete_quote(
    quote_id: str,
    service: QuoteService = Depends(get_quote_service),
):
    deleted = service.delete_quote(quote_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Quote not found",
        )

    return {
        "success": True,
    }


@router.get("/semantic-search")
def semantic_search(
    query: str = Query(...),
    service: QuoteService = Depends(get_quote_service),
):
    semantic = SemanticSearchService(service.repository)

    return semantic.search(query)
