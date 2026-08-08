from __future__ import annotations

import httpx

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


class NotionAPIError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Notion API error {status_code}: {detail}")


class NotionClient:
    """Thin wrapper around the Notion REST API for a single user's token."""

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        json: dict | None = None,
    ) -> dict:
        response = httpx.request(
            method,
            f"{NOTION_API_BASE}{path}",
            headers=self._headers(),
            json=json,
            timeout=15.0,
        )

        if response.status_code >= 400:
            raise NotionAPIError(response.status_code, response.text)

        return response.json()

    def query_database(
        self,
        database_id: str,
        filter_: dict | None = None,
    ) -> list[dict]:
        payload: dict = {}

        if filter_ is not None:
            payload["filter"] = filter_

        data = self._request(
            "POST",
            f"/databases/{database_id}/query",
            json=payload,
        )

        return data.get("results", [])

    def create_page(
        self,
        database_id: str,
        properties: dict,
    ) -> dict:
        return self._request(
            "POST",
            "/pages",
            json={
                "parent": {"database_id": database_id},
                "properties": properties,
            },
        )

    def update_page(
        self,
        page_id: str,
        properties: dict,
    ) -> dict:
        return self._request(
            "PATCH",
            f"/pages/{page_id}",
            json={"properties": properties},
        )
