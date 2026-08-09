from __future__ import annotations

from typing import Any

from app.schemas.web_search.quote import WebQuoteResult
from app.services.web_search.provider import WebQuoteProvider

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None


class TavilyQuoteProvider(WebQuoteProvider):
    """
    Web quote provider backed by Tavily Search.
    """

    def __init__(self) -> None:
        self.api_key = ""
        self.search_depth = "advanced"

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[WebQuoteResult]:

        query = query.strip()

        if not query or limit < 1:
            return []

        if not self.api_key:
            return []

        if TavilyClient is None:
            return []

        try:
            client = TavilyClient(api_key=self.api_key)

            response = client.search(
                query=query,
                search_depth=self.search_depth,
                max_results=limit,
            )
        except Exception:
            return []

        if not isinstance(response, dict):
            return []

        raw_results = response.get("results", [])

        if not isinstance(raw_results, list):
            return []

        results: list[WebQuoteResult] = []

        for item in raw_results:
            if not isinstance(item, dict):
                continue

            text = str(item.get("content") or "").strip()
            url = str(item.get("url") or "").strip()

            if not text or not url:
                continue

            results.append(
                WebQuoteResult(
                    text=text,
                    source="Tavily Search",
                    url=url,
                    score=item.get("score"),
                )
            )

            if len(results) >= limit:
                break

        return results
