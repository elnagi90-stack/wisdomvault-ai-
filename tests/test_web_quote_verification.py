from __future__ import annotations

from unittest.mock import Mock

from app.schemas.web_search.quote import WebQuoteResult
from app.services.web_search.service import WebSearchService


def _provider(*results: WebQuoteResult) -> Mock:
    provider = Mock()
    provider.search.return_value = list(results)
    return provider


def test_search_never_returns_provider_snippet_when_page_fetch_fails() -> None:
    provider = _provider(
        WebQuoteResult(
            text="This is only a search engine snippet.",
            source="Google Search",
            url="https://example.com/quote",
        )
    )

    service = WebSearchService(providers=[provider])

    service.page_extractor.extract_content = Mock(return_value=None)

    service.ranker.rank = Mock(
        side_effect=lambda query, results, limit: results[:limit]
    )

    results = service.search("wisdom", limit=5)

    assert results == []


def test_search_accepts_quote_extracted_from_real_page() -> None:
    provider = _provider(
        WebQuoteResult(
            text="Search snippet that must not be trusted.",
            source="Google Search",
            url="https://example.com/quote",
        )
    )

    service = WebSearchService(providers=[provider])

    page = Mock()
    page.html = "<blockquote>Real wisdom lives in action.</blockquote>"
    page.text = "Real wisdom lives in action."

    service.page_extractor.extract_content = Mock(return_value=page)

    metadata = Mock()
    metadata.author = "Example Author"
    metadata.book = "Example Book"
    service.metadata_extractor.extract = Mock(return_value=metadata)

    service.ranker.rank = Mock(
        side_effect=lambda query, results, limit: results[:limit]
    )

    results = service.search("wisdom", limit=5)

    assert len(results) == 1
    assert results[0].text == "Real wisdom lives in action."
    assert results[0].author == "Example Author"
    assert results[0].book == "Example Book"
    assert results[0].url == "https://example.com/quote"


def test_search_does_not_use_provider_text_when_page_contains_no_quotes() -> None:
    provider = _provider(
        WebQuoteResult(
            text="AI/search provider summary pretending to be a quote.",
            source="Tavily Search",
            url="https://example.com/page",
        )
    )

    service = WebSearchService(providers=[provider])

    page = Mock()
    page.html = "<main>This page contains an ordinary article but no quote.</main>"
    page.text = "This page contains an ordinary article but no quote."

    service.page_extractor.extract_content = Mock(return_value=page)

    service.ranker.rank = Mock(
        side_effect=lambda query, results, limit: results[:limit]
    )

    results = service.search("wisdom", limit=5)

    assert results == []


def test_quote_extractor_supports_curly_quotes() -> None:
    from app.services.web_search.quote_extractor import QuoteExtractor

    extractor = QuoteExtractor()

    results = extractor.extract(
        "The author wrote: “Wisdom grows when knowledge is put into practice.”"
    )

    assert results == [
        "Wisdom grows when knowledge is put into practice."
    ]
