from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.core.dependencies import get_author_service
from app.schemas.author import (
    AuthorCreate,
    AuthorResponse,
    AuthorUpdate,
)
from app.services.author_service import AuthorService

router = APIRouter(
    prefix="/authors",
    tags=["Authors"],
)


@router.get(
    "",
    response_model=list[AuthorResponse],
)
def list_authors(
    service: AuthorService = Depends(get_author_service),
):
    return service.list_authors()


@router.get(
    "/search",
    response_model=list[AuthorResponse],
)
def search_authors(
    q: str = Query(..., min_length=1),
    service: AuthorService = Depends(get_author_service),
):
    return service.search_authors(q)


@router.post(
    "",
    response_model=AuthorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_author(
    payload: AuthorCreate,
    service: AuthorService = Depends(get_author_service),
):
    try:
        return service.create_author(
            name=payload.name,
            bio=payload.bio,
            nationality=payload.nationality,
            birth_year=payload.birth_year,
            death_year=payload.death_year,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/{author_id}",
    response_model=AuthorResponse,
)
def get_author(
    author_id: str,
    service: AuthorService = Depends(get_author_service),
):
    author = service.get_author(author_id)

    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found",
        )

    return author


@router.put(
    "/{author_id}",
    response_model=AuthorResponse,
)
def update_author(
    author_id: str,
    payload: AuthorUpdate,
    service: AuthorService = Depends(get_author_service),
):
    try:
        author = service.update_author(
            author_id,
            payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found",
        )

    return author


@router.delete(
    "/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_author(
    author_id: str,
    service: AuthorService = Depends(get_author_service),
):
    deleted = service.delete_author(author_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)