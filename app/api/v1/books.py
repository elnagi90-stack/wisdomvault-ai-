from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_book_service
from app.schemas.book import BookCreate, BookResponse
from app.services.book_service import BookService

router = APIRouter(
    prefix="/books",
    tags=["Books"],
)


@router.get(
    "",
    response_model=list[BookResponse],
)
def list_books(
    service: BookService = Depends(get_book_service),
):
    return service.list_books()


@router.post(
    "",
    response_model=BookResponse,
)
def create_book(
    payload: BookCreate,
    service: BookService = Depends(get_book_service),
):
    return service.create_book(
        title=payload.title,
        author_id=str(payload.author_id) if payload.author_id else None,
        publisher=payload.publisher,
        publication_year=payload.publication_year,
        isbn=payload.isbn,
        language=payload.language,
        cover_image=payload.cover_image,
    )


@router.get(
    "/{book_id}",
    response_model=BookResponse,
)
def get_book(
    book_id: str,
    service: BookService = Depends(get_book_service),
):
    book = service.get_book(book_id)

    if book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    return book


@router.delete(
    "/{book_id}",
)
def delete_book(
    book_id: str,
    service: BookService = Depends(get_book_service),
):
    deleted = service.delete_book(book_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    return {"success": True}
