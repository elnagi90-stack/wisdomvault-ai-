from __future__ import annotations

from app.schemas.web_search.quote import WebQuoteResult
from app.services.web_search.bing_provider import BingQuoteProvider
from app.services.web_search.google_provider import GoogleQuoteProvider
from app.services.web_search.goodreads_provider import GoodreadsQuoteProvider
from app.services.web_search.metadata.extractor import PageMetadataExtractor
from app.services.web_search.page_extractor import WebPageExtractor
from app.services.web_search.provider import WebQuoteProvider
from app.services.web_search.query_generator import QueryGenerator
from app.services.web_search.quote_extractor import QuoteExtractor
from app.services.web_search.quote_validator import QuoteValidator
from app.services.web_search.ranker import WebQuoteRanker
from app.services.web_search.tavily_provider import TavilyQuoteProvider


class WebSearchService:
    """
    Search the web for quotes similar to a user-provided quote.

    Critical trust rule:
    a provider search result is a DISCOVERY RESULT, not a verified quote.

    A provider may return a search-engine snippet, an AI-generated summary,
    or arbitrary page text. Therefore provider text is never returned as a
    quote when a URL exists.

    A candidate becomes eligible only after:
        search provider -> real page fetch -> quote extraction -> validation

    This prevents Google/Tavily/Bing snippets from being presented to the
    user as if they were verbatim quotations.
    """

    MAX_PAGES_TO_EXTRACT = 20
    PAGE_MAX_CHARS = 100_000

    def __init__(
        self,
        providers: list[WebQuoteProvider] | None = None,
    ) -> None:
        self.providers = providers or [
            TavilyQuoteProvider(),
            GoodreadsQuoteProvider(),
            GoogleQuoteProvider(),
            BingQuoteProvider(),
        ]

        self.page_extractor = WebPageExtractor()
        self.quote_extractor = QuoteExtractor()
        self.metadata_extractor = PageMetadataExtractor()
        self.quote_validator = QuoteValidator()
        self.query_generator = QueryGenerator()
        self.ranker = WebQuoteRanker()

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[WebQuoteResult]:
        query = query.strip()

        if not query or limit < 1:
            return []

        candidate_limit = max(limit * 4, 30)

        search_queries = self.query_generator.generate(query) or [query]

        search_results: list[WebQuoteResult] = []

        # ---------------------------------------------------------
        # 1. Discovery
        # ---------------------------------------------------------
        #
        # Providers are discovery mechanisms only.
        # Their "text" field is NOT trusted as a final quote.
        # ---------------------------------------------------------

        for search_query in search_queries:
            for provider in self.providers:
                try:
                    provider_results = provider.search(
                        search_query,
                        candidate_limit,
                    )
                except Exception:
                    provider_results = []

                search_results.extend(provider_results)

        if not search_results:
            return []

        # ---------------------------------------------------------
        # 2. Deduplicate discovered pages
        # ---------------------------------------------------------

        unique_search_results: list[WebQuoteResult] = []
        seen_urls: set[str] = set()
        seen_text_without_url: set[str] = set()

        for result in search_results:
            normalized_url = (
                result.url.strip().lower()
                if result.url
                else ""
            )

            normalized_text = " ".join(
                result.text.lower().split()
            )

            if normalized_url:
                if normalized_url in seen_urls:
                    continue

                seen_urls.add(normalized_url)
                unique_search_results.append(result)
                continue

            # A result without a URL cannot be independently verified.
            # Keep it out of the final pipeline entirely.
            if normalized_text in seen_text_without_url:
                continue

            seen_text_without_url.add(normalized_text)

        if not unique_search_results:
            return []

        # ---------------------------------------------------------
        # 3. Fetch pages and extract VERIFIED quote candidates
        # ---------------------------------------------------------

        extracted_quotes: list[WebQuoteResult] = []
        pages_processed = 0

        for result in unique_search_results:
            if not result.url:
                # No source URL = no independent verification.
                continue

            if pages_processed >= self.MAX_PAGES_TO_EXTRACT:
                break

            pages_processed += 1

            try:
                page_content = self.page_extractor.extract_content(
                    result.url,
                    max_chars=self.PAGE_MAX_CHARS,
                )
            except Exception:
                page_content = None

            # If the page cannot be fetched, the provider snippet is NOT
            # allowed to survive as a fallback.
            if page_content is None:
                continue

            quotes: list[str] = []

            # Prefer semantic HTML quote elements from the original page.
            try:
                quotes = self.quote_extractor.extract_html(
                    page_content.html,
                    limit=candidate_limit,
                )
            except Exception:
                quotes = []

            # Fallback to quotation marks in cleaned readable text.
            if not quotes:
                try:
                    quotes = self.quote_extractor.extract(
                        page_content.text,
                        limit=candidate_limit,
                    )
                except Exception:
                    quotes = []

            if not quotes:
                # Again: do NOT fall back to provider content.
                continue

            try:
                page_metadata = self.metadata_extractor.extract(
                    page_content.text,
                )
            except Exception:
                page_metadata = None

            for quote in quotes:
                if not self.quote_validator.is_valid(quote):
                    continue

                # The quote is verified because it was extracted directly
                # from the fetched source page, not from the search snippet.
                extracted_quotes.append(
                    WebQuoteResult(
                        text=quote,
                        author=(
                            (
                                page_metadata.author
                                if page_metadata
                                else None
                            )
                            or result.author
                        ),
                        book=(
                            (
                                page_metadata.book
                                if page_metadata
                                else None
                            )
                            or result.book
                        ),
                        source=result.source,
                        url=result.url,
                        score=None,
                    )
                )

        if not extracted_quotes:
            return []

        # ---------------------------------------------------------
        # 4. Final deduplication
        # ---------------------------------------------------------

        unique_quotes: list[WebQuoteResult] = []
        seen_quotes: set[str] = set()

        for result in extracted_quotes:
            normalized = " ".join(
                result.text.lower().split()
            )

            if not normalized or normalized in seen_quotes:
                continue

            seen_quotes.add(normalized)
            unique_quotes.append(result)

        if not unique_quotes:
            return []

        # ---------------------------------------------------------
        # 5. Semantic ranking
        # ---------------------------------------------------------

        return self.ranker.rank(
            query=query,
            results=unique_quotes,
            limit=limit,
        )
