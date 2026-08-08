from __future__ import annotations

from app.schemas.web_search.quote import WebQuoteResult
from app.services.web_search.google_provider import GoogleQuoteProvider
from app.services.web_search.goodreads_provider import GoodreadsQuoteProvider
from app.services.web_search.provider import WebQuoteProvider
from app.services.web_search.ranker import WebQuoteRanker


class WebSearchService:
    """
    Orchestrates multiple web quote providers.

    The service is intentionally unaware of provider-specific
    scraping logic. Providers return normalized WebQuoteResult
    objects, which are then deduplicated and semantically ranked.
    """

    def __init__(
        self,
        providers: list[WebQuoteProvider] | None = None,
    ) -> None:
        self.providers = providers or [
            GoodreadsQuoteProvider(),
            GoogleQuoteProvider(),
        ]

        self.ranker = WebQuoteRanker()

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[WebQuoteResult]:

        query = query.strip()

        if not query or limit < 1:
            return []

        # -------------------------------------------------
        # Candidate pool
        #
        # Fetch more candidates than the requested final
        # limit so semantic ranking has meaningful choices.
        # -------------------------------------------------

        candidate_limit = max(limit * 2, 20)

        results: list[WebQuoteResult] = []

        # -------------------------------------------------
        # Collect from all providers
        # -------------------------------------------------

        for provider in self.providers:
            try:
                provider_results = provider.search(
                    query,
                    candidate_limit,
                )
            except Exception:
                # One broken provider must not bring down
                # the entire web-search system.
                provider_results = []

            results.extend(provider_results)

        # -------------------------------------------------
        # Deduplicate
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Semantic ranking
        # -------------------------------------------------

        return self.ranker.rank(
            query=query,
            results=unique,
            limit=limit,
        )
