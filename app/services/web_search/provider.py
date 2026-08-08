from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.web_search.quote import WebQuoteResult


class WebQuoteProvider(ABC):
    """
    Base interface for web quote sources.

    Every provider receives a search query and returns
    normalized WebQuoteResult objects.
    """

    @abstractmethod
    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[WebQuoteResult]:
        raise NotImplementedError
