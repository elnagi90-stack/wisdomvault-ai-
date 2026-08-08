from __future__ import annotations

from unittest.mock import Mock

from app.schemas.web_search.quote import WebQuoteResult
from app.services.web_search.service import WebSearchService
from app.services.web_search.metadata.extractor import PageMetadata


def _provider(*results: WebQuoteResult) -> Mock:
    provider = Mock()
    provider.search.return_value = list(results)
    return provider


def test_search_extracts_quotes_from_discovered_pages() -> None:
    provider = _provider(
        WebQuoteResult(
            text="Search result snippet",
            source="Google Search",
            url="https://example.com/article",
        )
    )

    service = WebSearchService(providers=[provider])

    service.page_extractor.extract = Mock(
        return_value=(
            '"The best way to predict the future is to create it." '
            'Some unrelated page text.'
        )
    )

    service.ranker.rank = Mock(
        side_effect=lambda query, results, limit: results[:limit]
    )

    results = service.search(
        query="predict the future",
        limit=10,
    )

    assert len(results) == 1
    assert results[0].text == (
        "The best way to predict the future is to create it."
    )
    assert results[0].source == "Google Search"
    assert results[0].url == "https://example.com/article"


def test_search_preserves_provider_result_when_page_extraction_fails() -> None:
    provider = _provider(
        WebQuoteResult(
            text="Knowledge speaks, wisdom listens",
            author="Jimi Hendrix",
            source="Google Search",
            url="https://example.com/quote",
        )
    )

    service = WebSearchService(providers=[provider])

    service.page_extractor.extract = Mock(return_value="")

    service.ranker.rank = Mock(
        side_effect=lambda query, results, limit: results[:limit]
    )

    results = service.search(
        query="wisdom",
        limit=10,
    )

    assert len(results) == 1
    assert results[0].text == "Knowledge speaks, wisdom listens"
    assert results[0].author == "Jimi Hendrix"
    assert results[0].source == "Google Search"


def test_search_deduplicates_extracted_quotes() -> None:
    provider = _provider(
        WebQuoteResult(
            text="Snippet one",
            source="Google Search",
            url="https://example.com/one",
        ),
        WebQuoteResult(
            text="Snippet two",
            source="Bing Search",
            url="https://example.com/two",
        ),
    )

    service = WebSearchService(providers=[provider])

    service.page_extractor.extract = Mock(
        side_effect=[
            '"The same wisdom applies everywhere."',
            '"The same wisdom applies everywhere."',
        ]
    )

    service.ranker.rank = Mock(
        side_effect=lambda query, results, limit: results[:limit]
    )

    results = service.search(
        query="wisdom",
        limit=10,
    )

    assert len(results) == 1
    assert results[0].text == "The same wisdom applies everywhere."


def test_search_respects_limit_after_ranking() -> None:
    provider = _provider(
        WebQuoteResult(
            text="Search result",
            source="Google Search",
            url="https://example.com/article",
        )
    )

    service = WebSearchService(providers=[provider])

    service.page_extractor.extract = Mock(
        return_value=(
            '"First meaningful quotation here." '
            '"Second meaningful quotation here." '
            '"Third meaningful quotation here."'
        )
    )

    service.ranker.rank = Mock(
        side_effect=lambda query, results, limit: results[:limit]
    )

    results = service.search(
        query="meaningful quotation",
        limit=2,
    )

    assert len(results) == 2


def test_search_survives_provider_failure() -> None:
    broken_provider = Mock()
    broken_provider.search.side_effect = RuntimeError(
        "provider unavailable"
    )

    working_provider = _provider(
        WebQuoteResult(
            text="A useful quotation",
            source="Bing Search",
            url="https://example.com/useful",
        )
    )

    service = WebSearchService(
        providers=[
            broken_provider,
            working_provider,
        ]
    )

    service.page_extractor.extract = Mock(
        return_value='"A useful quotation from a page."'
    )

    service.ranker.rank = Mock(
        side_effect=lambda query, results, limit: results[:limit]
    )

    results = service.search(
        query="useful quotation",
        limit=10,
    )

    assert len(results) == 1
    assert results[0].text == "A useful quotation from a page."


def test_search_passes_query_to_ranker() -> None:
    provider = _provider(
        WebQuoteResult(
            text="A meaningful quote",
            source="Google Search",
            url="https://example.com/quote",
        )
    )

    service = WebSearchService(providers=[provider])

    service.page_extractor.extract = Mock(
        return_value='"A meaningful quote for testing."'
    )

    service.ranker.rank = Mock(
        side_effect=lambda query, results, limit: results[:limit]
    )

    service.search(
        query="  meaningful quote  ",
        limit=5,
    )

    service.ranker.rank.assert_called_once()

    call = service.ranker.rank.call_args

    assert call.kwargs["query"] == "meaningful quote"
    assert call.kwargs["limit"] == 5

def test_search_uses_page_metadata_for_extracted_quote() -> None:
    provider = _provider(
        WebQuoteResult(
            text="A search snippet",
            author=None,
            book=None,
            source="Google Search",
            url="https://example.com/quote",
        )
    )

    service = WebSearchService(providers=[provider])

    service.page_extractor.extract = Mock(
        return_value='"The important thing is to never stop learning."'
    )

    service.quote_extractor.extract = Mock(
        return_value=[
            "The important thing is to never stop learning."
        ]
    )

    service.metadata_extractor.extract = Mock(
        return_value=PageMetadata(
            title="Great Quotes from The Alchemist",
            author="Paulo Coelho",
            book="The Alchemist",
        )
    )

    service.ranker.rank = Mock(
        side_effect=lambda query, results, limit: results[:limit]
    )

    results = service.search(
        query="learning",
        limit=10,
    )

    assert len(results) == 1
    assert results[0].text == (
        "The important thing is to never stop learning."
    )
    assert results[0].author == "Paulo Coelho"
    assert results[0].book == "The Alchemist"
    assert results[0].source == "Google Search"
    assert results[0].url == "https://example.com/quote"