from __future__ import annotations

import base64
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx
import jwt

from app.core.config import Settings

NOTION_AUTHORIZE_URL = "https://api.notion.com/v1/oauth/authorize"
NOTION_TOKEN_URL = "https://api.notion.com/v1/oauth/token"

STATE_ALGORITHM = "HS256"
STATE_EXPIRE_MINUTES = 10


class NotionOAuthError(Exception):
    pass


def create_state_token(user_id: str, settings: Settings) -> str:
    """Short-lived, signed token binding this OAuth attempt to a user.

    Notion's redirect back to us has no session to rely on, so this
    signed state parameter is what prevents a CSRF attacker from
    tricking a different logged-in user into linking their Notion
    account to the attacker's.
    """
    expire = datetime.now(UTC) + timedelta(minutes=STATE_EXPIRE_MINUTES)

    payload = {
        "sub": user_id,
        "purpose": "notion_oauth",
        "exp": expire,
    }

    return jwt.encode(payload, settings.secret_key, algorithm=STATE_ALGORITHM)


def verify_state_token(state: str, settings: Settings) -> str | None:
    """Returns the user_id the state token was issued for, or None."""
    try:
        payload = jwt.decode(
            state,
            settings.secret_key,
            algorithms=[STATE_ALGORITHM],
        )
    except jwt.PyJWTError:
        return None

    if payload.get("purpose") != "notion_oauth":
        return None

    return payload.get("sub")


def build_authorize_url(state: str, settings: Settings) -> str:
    if not settings.notion_client_id:
        raise NotionOAuthError(
            "NOTION_CLIENT_ID is not configured on the server."
        )

    params = {
        "client_id": settings.notion_client_id,
        "redirect_uri": settings.notion_redirect_uri,
        "response_type": "code",
        "owner": "user",
        "state": state,
    }

    return f"{NOTION_AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code_for_token(code: str, settings: Settings) -> dict:
    if not settings.notion_client_id or not settings.notion_client_secret:
        raise NotionOAuthError(
            "Notion OAuth client credentials are not configured on the server."
        )

    basic = base64.b64encode(
        f"{settings.notion_client_id}:{settings.notion_client_secret}".encode()
    ).decode()

    response = httpx.post(
        NOTION_TOKEN_URL,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/json",
        },
        json={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.notion_redirect_uri,
        },
        timeout=15.0,
    )

    if response.status_code >= 400:
        raise NotionOAuthError(
            f"Notion token exchange failed ({response.status_code}): {response.text}"
        )

    return response.json()
