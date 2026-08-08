from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import (
    get_current_user,
    get_db,
    get_notion_sync_service,
    get_quote_service,
)
from app.integrations.notion.oauth import (
    NotionOAuthError,
    build_authorize_url,
    create_state_token,
    exchange_code_for_token,
    verify_state_token,
)
from app.integrations.notion.sync import (
    NotionNotConnectedError,
    NotionSyncService,
)
from app.models.user import User
from app.schemas.quote import QuoteResponse
from app.services.quote_service import QuoteService

router = APIRouter(
    prefix="/notion",
    tags=["Notion"],
)


class NotionDatabaseConfig(BaseModel):
    database_id: str


class NotionStatus(BaseModel):
    connected: bool
    workspace_id: str | None = None
    database_configured: bool = False


@router.get(
    "/connect",
)
def connect_notion(
    current_user: User = Depends(get_current_user),
):
    """Returns the URL the client should send the user to on Notion."""
    state = create_state_token(current_user.id, settings)

    try:
        url = build_authorize_url(state, settings)
    except NotionOAuthError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {"authorize_url": url}


@router.get(
    "/callback",
)
def notion_callback(
    code: str,
    state: str,
    session: Session = Depends(get_db),
):
    """Notion redirects the user's browser here after they approve access."""
    user_id = verify_state_token(state, settings)

    if user_id is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OAuth state.",
        )

    user = session.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        token_data = exchange_code_for_token(code, settings)
    except NotionOAuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    user.notion_access_token = token_data.get("access_token")
    user.notion_workspace_id = token_data.get("workspace_id")
    session.commit()

    return {"connected": True, "workspace_id": user.notion_workspace_id}


@router.get(
    "/status",
    response_model=NotionStatus,
)
def notion_status(
    current_user: User = Depends(get_current_user),
):
    return NotionStatus(
        connected=bool(current_user.notion_access_token),
        workspace_id=current_user.notion_workspace_id,
        database_configured=bool(current_user.notion_quotes_database_id),
    )


@router.post(
    "/database",
    response_model=NotionStatus,
)
def set_notion_database(
    payload: NotionDatabaseConfig,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.notion_quotes_database_id = payload.database_id
    session.commit()

    return NotionStatus(
        connected=bool(current_user.notion_access_token),
        workspace_id=current_user.notion_workspace_id,
        database_configured=True,
    )


@router.post(
    "/sync/{quote_id}",
    response_model=QuoteResponse,
)
def sync_quote_to_notion(
    quote_id: str,
    quote_service: QuoteService = Depends(get_quote_service),
    sync_service: NotionSyncService = Depends(get_notion_sync_service),
    current_user: User = Depends(get_current_user),
):
    quote = quote_service.get_quote(quote_id)

    if quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")

    try:
        return sync_service.sync_quote(quote, current_user)
    except NotionNotConnectedError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
