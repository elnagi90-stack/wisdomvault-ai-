from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_category_service
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.category_service import CategoryService

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get(
    "",
    response_model=list[CategoryResponse],
)
def list_categories(
    service: CategoryService = Depends(get_category_service),
):
    return service.list_categories()


@router.get(
    "/search",
    response_model=list[CategoryResponse],
)
def search_categories(
    q: str = Query(..., min_length=1),
    service: CategoryService = Depends(get_category_service),
):
    return service.search_categories(q)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=201,
)
def create_category(
    payload: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    try:
        return service.create_category(
            name=payload.name,
            description=payload.description,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: str,
    service: CategoryService = Depends(get_category_service),
):
    category = service.get_category(category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return category


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: str,
    payload: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
):
    try:
        category = service.update_category(
            category_id,
            payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return category


@router.delete(
    "/{category_id}",
)
def delete_category(
    category_id: str,
    service: CategoryService = Depends(get_category_service),
):
    deleted = service.delete_category(category_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return {
        "success": True,
    }
