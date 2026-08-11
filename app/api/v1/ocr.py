from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile

from app.api.v1.web_search import get_web_search_service
from app.core.dependencies import get_current_user, get_ocr_service
from app.models.user import User
from app.ocr.engine import OcrEngineUnavailableError
from app.schemas.ocr import OcrExtractResponse
from app.schemas.web_search.quote import WebQuoteResult
from app.services.ocr_service import OcrService, UnsupportedImageError
from app.services.web_search.service import WebSearchService

router = APIRouter(
    prefix="/ocr",
    tags=["OCR"],
)


def _extract(
    file: UploadFile,
    ocr_service: OcrService,
) -> str:
    image_bytes = file.file.read()

    try:
        return ocr_service.extract_text_from_image(
            image_bytes,
            content_type=file.content_type,
            original_filename=file.filename,
        )
    except UnsupportedImageError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except OcrEngineUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.post(
    "/extract",
    response_model=OcrExtractResponse,
)
def extract_text_from_image(
    file: UploadFile,
    ocr_service: OcrService = Depends(get_ocr_service),
    current_user: User = Depends(get_current_user),
):
    """
    Extracts text from an uploaded image only.

    Does not search or save anything.
    """
    text = _extract(file, ocr_service)

    return OcrExtractResponse(
        text=text,
        saved_image_path=None,
    )


@router.post(
    "/search",
    response_model=list[WebQuoteResult],
)
def search_from_image(
    file: UploadFile,
    limit: int = Query(default=5, ge=1, le=20),
    ocr_service: OcrService = Depends(get_ocr_service),
    web_search_service: WebSearchService = Depends(get_web_search_service),
    current_user: User = Depends(get_current_user),
):
    """
    OCR + discovery pipeline.

    Extracts text from the uploaded image and feeds it directly
    into the same WebSearchService used by /web-search and
    the Telegram /findsimilar command.
    """
    text = _extract(file, ocr_service)

    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="No text could be extracted from this image.",
        )

    return web_search_service.search(text, limit=limit)
