from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_tag_service
from app.schemas.tag import (
    TagCreate,
    TagResponse,
    TagUpdate,
)
from app.services.tag_service import TagService

router = APIRouter(
    prefix="/tags",
    tags=["Tags"],
)


@router.get(
    "",
    response_model=list[TagResponse],
)
def list_tags(
    service: TagService = Depends(get_tag_service),
):
    return service.list_tags()


@router.get(
    "/search",
    response_model=list[TagResponse],
)
def search_tags(
    q: str = Query(..., min_length=1),
    service: TagService = Depends(get_tag_service),
):
    return service.search_tags(q)


@router.post(
    "",
    response_model=TagResponse,
    status_code=201,
)
def create_tag(
    payload: TagCreate,
    service: TagService = Depends(get_tag_service),
):
    try:
        return service.create_tag(
            name=payload.name,
            color=payload.color,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/{tag_id}",
    response_model=TagResponse,
)
def get_tag(
    tag_id: str,
    service: TagService = Depends(get_tag_service),
):
    tag = service.get_tag(tag_id)

    if tag is None:
        raise HTTPException(
            status_code=404,
            detail="Tag not found",
        )

    return tag


@router.put(
    "/{tag_id}",
    response_model=TagResponse,
)
def update_tag(
    tag_id: str,
    payload: TagUpdate,
    service: TagService = Depends(get_tag_service),
):
    try:
        tag = service.update_tag(
            tag_id,
            payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if tag is None:
        raise HTTPException(
            status_code=404,
            detail="Tag not found",
        )

    return tag


@router.delete(
    "/{tag_id}",
)
def delete_tag(
    tag_id: str,
    service: TagService = Depends(get_tag_service),
):
    deleted = service.delete_tag(tag_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Tag not found",
        )

    return {
        "success": True,
    }