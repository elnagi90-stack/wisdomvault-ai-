from __future__ import annotations

from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from app.schemas.web_search.quote import WebQuoteResult
from app.services.web_search.provider import WebQuoteProvider


class BingQuoteProvider(WebQuoteProvider):
    """
    Web quote provider backed by Bing Search.
    """

    def __init__(self) -> None:
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[WebQuoteResult]:

        query = query.strip()

        if not query or limit < 1:
            return []

        url = (
            "https://www.bing.com/search?q="
            + quote_plus(query)
            + "&count=20"
        )

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=15,
            )
            response.raise_for_status()
        except requests.RequestException:
            return []

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        results: list[WebQuoteResult] = []
        seen: set[str] = set()

        for item in soup.select("li.b_algo"):

            if len(results) >= limit:
                break

            title = item.select_one("h2")

            if not title:
                continue

            link = title.select_one("a")

            if link is None:
                continue

            href = link.get("href")

            if not href or not href.startswith("http"):
                continue

            snippet_element = item.select_one(
                ".b_caption p, .b_algoSlug"
            )

            snippet = (
                snippet_element.get_text(
                    " ",
                    strip=True,
                )
                if snippet_element
                else ""
            )

            if not snippet:
                continue

            normalized = " ".join(
                snippet.lower().split()
            )

            if normalized in seen:
                continue

            seen.add(normalized)

            results.append(
                WebQuoteResult(
                    text=snippet,
                    source="Bing Search",
                    url=href,
                    score=None,
                )
            )

        return results
