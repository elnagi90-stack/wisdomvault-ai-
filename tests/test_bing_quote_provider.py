from unittest.mock import Mock, patch

from app.services.web_search.bing_provider import BingQuoteProvider


def test_bing_provider_returns_results():
    html = """
    <html>
        <body>
            <li class="b_algo">
                <h2>
                    <a href="https://example.com/quote">
                        Example Quote
                    </a>
                </h2>
                <div class="b_caption">
                    <p>
                        The important thing is to never stop learning.
                    </p>
                </div>
            </li>
        </body>
    </html>
    """

    response = Mock()
    response.raise_for_status.return_value = None
    response.text = html

    with patch(
        "app.services.web_search.bing_provider.requests.get",
        return_value=response,
    ):
        provider = BingQuoteProvider()

        results = provider.search(
            query="never stop learning",
            limit=10,
        )

    assert len(results) == 1
    assert (
        results[0].text
        == "The important thing is to never stop learning."
    )
    assert results[0].source == "Bing Search"
    assert results[0].url == "https://example.com/quote"


def test_bing_provider_rejects_empty_query():
    provider = BingQuoteProvider()

    assert provider.search("", 10) == []
    assert provider.search("   ", 10) == []


def test_bing_provider_rejects_invalid_limit():
    provider = BingQuoteProvider()

    assert provider.search("test", 0) == []


def test_bing_provider_handles_request_failure():
    import requests

    with patch(
        "app.services.web_search.bing_provider.requests.get",
        side_effect=requests.RequestException(),
    ):
        provider = BingQuoteProvider()

        results = provider.search(
            query="test quote",
            limit=10,
        )

    assert results == []
