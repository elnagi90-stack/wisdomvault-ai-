from __future__ import annotations

from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from app.schemas.web_search.quote import WebQuoteResult
from app.services.web_search.goodreads import GoodreadsQuoteScraper


class WebSearchService:
    def __init__(self) -> None:
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

        self.goodreads = GoodreadsQuoteScraper()

    def _google_search(
        self,
        query: str,
        limit: int,
    ) -> list[WebQuoteResult]:

        url = (
            "https://www.google.com/search?q="
            + quote_plus(query)
            + "&num=20"
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

        candidates = soup.select("div.MjjYud")

        if not candidates:
            candidates = soup.select("div.g")

        for item in candidates:

            if len(results) >= limit:
                break

            title = item.select_one("h3")

            if not title:
                continue

            link = title.find_parent("a")

            if link is None:
                link = item.select_one("a")

            if link is None:
                continue

            href = link.get("href")

            if not href:
                continue

            if href.startswith("/url?q="):
                href = href.split(
                    "/url?q=",
                    1,
                )[1].split("&", 1)[0]

            if not href.startswith("http"):
                continue

            snippet_element = item.select_one(
                ".VwiC3b, .yXK7lf, .IsZvec"
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

            results.append(
                WebQuoteResult(
                    text=snippet,
                    source="Google Search",
                    url=href,
                    score=None,
                )
            )

        return results

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[WebQuoteResult]:

        query = query.strip()

        if not query or limit < 1:
            return []

        results: list[WebQuoteResult] = []

        # Goodreads is currently the most reliable quote source.
        results.extend(
            self.goodreads.search(
                query,
                limit,
            )
        )

        # Google is supplemental.
        if len(results) < limit:

            remaining = limit - len(results)

            results.extend(
                self._google_search(
                    query,
                    remaining,
                )
            )

        # Deduplicate.
        unique: list[WebQuoteResult] = []
        seen: set[str] = set()

        for result in results:

            normalized = " ".join(
                result.text.lower().split()
            )

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(normalized)
            unique.append(result)

            if len(unique) >= limit:
                break

        return unique
