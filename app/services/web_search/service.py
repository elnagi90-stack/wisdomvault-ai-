from __future__ import annotations

from app.schemas.web_search.quote import WebQuoteResult
from app.services.web_search.google_provider import GoogleQuoteProvider
from app.services.web_search.goodreads_provider import GoodreadsQuoteProvider
from app.services.web_search.bing_provider import BingQuoteProvider
from app.services.web_search.page_extractor import WebPageExtractor
from app.services.web_search.quote_extractor import QuoteExtractor
from app.services.web_search.metadata.extractor import PageMetadataExtractor
from app.services.web_search.provider import WebQuoteProvider
from app.services.web_search.ranker import WebQuoteRanker

class WebSearchService:
    """
    Orchestrates web quote providers and extracts real quotes
    from discovered web pages before semantic ranking.
    """

    MAX_PAGES_TO_EXTRACT = 10
    PAGE_MAX_CHARS = 100_000

    def __init__(
        self,
        providers: list[WebQuoteProvider] | None = None,
    ) -> None:
        self.providers = providers or [
            GoodreadsQuoteProvider(),
            GoogleQuoteProvider(),
            BingQuoteProvider(),
        ]

        self.page_extractor = WebPageExtractor()
        self.quote_extractor = QuoteExtractor()
        self.metadata_extractor = PageMetadataExtractor()
        self.ranker = WebQuoteRanker()

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[WebQuoteResult]:

        query = query.strip()

        if not query or limit < 1:
            return []

        candidate_limit = max(limit * 2, 20)

        search_results: list[WebQuoteResult] = []

        # -------------------------------------------------
        # Search providers
        # -------------------------------------------------

        for provider in self.providers:
            try:
                provider_results = provider.search(
                    query,
                    candidate_limit,
                )
            except Exception:
                provider_results = []

            search_results.extend(provider_results)

        if not search_results:
            return []

        # -------------------------------------------------
        # Deduplicate search results
        # -------------------------------------------------

        unique_search_results: list[WebQuoteResult] = []
        seen_urls: set[str] = set()
        seen_text: set[str] = set()

        for result in search_results:

            normalized_text = " ".join(
                result.text.lower().split()
            )

            normalized_url = (
                result.url.strip().lower()
                if result.url
                else ""
            )

            if normalized_url and normalized_url in seen_urls:
                continue

            if normalized_text and normalized_text in seen_text:
                continue

            if normalized_url:
                seen_urls.add(normalized_url)

            if normalized_text:
                seen_text.add(normalized_text)

            unique_search_results.append(result)

        # -------------------------------------------------
        # Extract real quotes from discovered pages
        # -------------------------------------------------

        extracted_quotes: list[WebQuoteResult] = []

        pages_processed = 0

        for result in unique_search_results:

            # Provider-native results are valid candidates
            # even when no page URL exists.
            if not result.url:
                extracted_quotes.append(result)
                continue

            if pages_processed >= self.MAX_PAGES_TO_EXTRACT:
                extracted_quotes.append(result)
                continue

            pages_processed += 1

            try:
                page_text = self.page_extractor.extract(
                    result.url,
                    max_chars=self.PAGE_MAX_CHARS,
                )
            except Exception:
                page_text = ""

            # -------------------------------------------------
            # Fallback:
            # If the page cannot be fetched, preserve the
            # provider's original result instead of losing it.
            # -------------------------------------------------

            if not page_text:
                extracted_quotes.append(result)
                continue

            try:
                quotes = self.quote_extractor.extract(
                    page_text,
                    limit=candidate_limit,
                )
            except Exception:
                quotes = []

            # -------------------------------------------------
            # Another fallback:
            # Page was fetched, but no quote-like passages
            # were found. Preserve the provider result.
            # -------------------------------------------------

            if not quotes:
                extracted_quotes.append(result)
                continue

            try:
                page_metadata = self.metadata_extractor.extract(page_text)
            except Exception:
                page_metadata = None

            for quote in quotes:
                extracted_quotes.append(
                    WebQuoteResult(
                        text=quote,
                        author=(
                            (page_metadata.author if page_metadata else None)
                            or result.author
                        ),
                        book=(
                            (page_metadata.book if page_metadata else None)
                            or result.book
                        ),
                        source=result.source,
                        url=result.url,
                        score=None,
                    )
                )

        # -------------------------------------------------
        # Deduplicate final candidates
        # -------------------------------------------------

        unique_quotes: list[WebQuoteResult] = []
        seen_quotes: set[str] = set()

        for result in extracted_quotes:

            normalized = " ".join(
                result.text.lower().split()
            )

            if not normalized:
                continue

            if normalized in seen_quotes:
                continue

            seen_quotes.add(normalized)
            unique_quotes.append(result)

        if not unique_quotes:
            return []

        # -------------------------------------------------
        # Semantic ranking
        # -------------------------------------------------

        return self.ranker.rank(
            query=query,
            results=unique_quotes,
            limit=limit,
        )
