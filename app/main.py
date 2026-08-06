from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.v1 import api_router
from app.core.config import settings
from app.core.dependencies import get_knowledge_service
from app.core.logging import logger
from app.database.base import create_engine_from_settings, init_db
from app.database.session import build_session_factory
from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.knowledge import (
    KnowledgeEntryCreate,
    KnowledgeEntryResponse,
)
from app.services.ai_service import AiService
from app.services.knowledge_service import KnowledgeService
from app.services.ocr_service import OcrService
from app.services.search_service import SearchService
from app.services.storage_service import LocalStorageService

app = FastAPI(title=settings.app_name)

app.include_router(
    api_router,
    prefix="/api/v1",
)

allow_origins = ["*"] if settings.cors_allow_all else settings.allowed_origins or []

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine_from_settings(settings)
init_db(engine)

session_factory = build_session_factory(engine)

knowledge_repository = KnowledgeRepository(session_factory=lambda: session_factory())

knowledge_service = KnowledgeService(repository=knowledge_repository)

storage_service = LocalStorageService(base_path=settings.storage_path / "uploads")

ai_service = AiService()
ocr_service = OcrService()


def require_api_key(
    x_api_key: str | None = Header(default=None),
) -> None:
    if settings.api_key and (not x_api_key or x_api_key != settings.api_key):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid X-API-KEY header",
        )


@app.get("/")
def read_root() -> dict[str, str]:
    logger.info("Root endpoint requested")
    return {"message": "WisdomVault AI is running"}


@app.get("/health")
def health_check() -> dict[str, object]:
    return {
        "status": "ok",
        "app_env": settings.app_env.value,
        "database_url": settings.database_url,
    }


@app.post(
    "/knowledge",
    response_model=KnowledgeEntryResponse,
)
def create_knowledge_entry(
    payload: KnowledgeEntryCreate | None = None,
    title: str | None = Query(default=None),
    content: str | None = Query(default=None),
    service=Depends(get_knowledge_service),
    _=Depends(require_api_key),
) -> KnowledgeEntryResponse:
    if payload is not None:
        title_value = payload.title
        content_value = payload.content
    else:
        if title is None or content is None:
            raise HTTPException(
                status_code=422,
                detail="title and content are required",
            )

        title_value = title
        content_value = content

    entry = service.create_entry(
        title=title_value,
        content=content_value,
    )

    return KnowledgeEntryResponse.model_validate(entry)


@app.get(
    "/knowledge",
    response_model=list[KnowledgeEntryResponse],
)
def list_knowledge_entries(
    service=Depends(get_knowledge_service),
) -> list[KnowledgeEntryResponse]:
    entries = service.list_entries()

    return [KnowledgeEntryResponse.model_validate(entry) for entry in entries]


@app.get(
    "/search",
    response_model=list[KnowledgeEntryResponse],
)
def search_knowledge(
    query: str,
    service=Depends(get_knowledge_service),
) -> list[KnowledgeEntryResponse]:
    search_service = SearchService(service)

    entries = search_service.search(query)

    return [KnowledgeEntryResponse.model_validate(entry) for entry in entries]


@app.post("/upload")
def upload_text(
    filename: str,
    content: str,
    _=Depends(require_api_key),
) -> dict[str, object]:
    path = storage_service.save_bytes(
        filename,
        content.encode("utf-8"),
    )

    return {
        "filename": filename,
        "path": str(path),
    }


@app.get("/summary")
def get_summary(
    text: str,
) -> dict[str, str]:
    return {
        "summary": ai_service.summarize(text),
    }


@app.get("/ocr")
def get_ocr_preview() -> dict[str, str]:
    return {
        "result": ocr_service.extract_text(b"sample"),
    }


@app.get(
    "/ui",
    response_class=HTMLResponse,
)
def get_ui_page() -> HTMLResponse:
    html = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1">
<title>WisdomVault AI</title>

<style>
body{
    font-family:Arial,sans-serif;
    margin:2rem;
    background:#0f172a;
    color:#f8fafc;
}
.card{
    background:#111827;
    padding:1.5rem;
    border-radius:12px;
    max-width:720px;
}
code{
    background:#1f2937;
    padding:.2rem .4rem;
    border-radius:4px;
}
a{
    color:#38bdf8;
}
</style>

</head>

<body>

<div class="card">

<h1>WisdomVault AI</h1>

<p>
This is the lightweight browser UI
for the personal knowledge workspace.
</p>

<ul>
<li><a href="/health">Health</a></li>
<li><a href="/knowledge">Knowledge entries</a></li>
<li><a href="/search?query=fastapi">Search examples</a></li>
<li><a href="/docs">Swagger API</a></li>
<li><a href="/api/v1/quotes">Quotes API</a></li>
</ul>

<p>
You can also call the API endpoints directly
from the browser or a client like Postman.
</p>

</div>

</body>
</html>
"""

    return HTMLResponse(content=html)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
