from __future__ import annotations

from app.schemas.web_search.quote import WebQuoteResult
from app.services.web_search.goodreads import GoodreadsQuoteScraper
from app.services.web_search.provider import WebQuoteProvider


class GoodreadsQuoteProvider(WebQuoteProvider):
    """
    Web quote provider backed by Goodreads.
    """

    def __init__(self) -> None:
        self.scraper = GoodreadsQuoteScraper()

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[WebQuoteResult]:
        return self.scraper.search(
            query=query,
            limit=limit,
        )
