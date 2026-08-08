from unittest.mock import Mock, patch

from app.services.web_search.google_provider import GoogleQuoteProvider


def test_google_provider_returns_quotes_from_search_results():
    html = """
    <html>
        <body>
            <div class="MjjYud">
                <a href="https://example.com/quote">
                    <h3>Example Quote</h3>
                </a>
                <div class="VwiC3b">
                    True happiness comes from appreciating what you have.
                </div>
            </div>
        </body>
    </html>
    """

    response = Mock()
    response.text = html
    response.raise_for_status.return_value = None

    with patch(
        "app.services.web_search.google_provider.requests.get",
        return_value=response,
    ):
        provider = GoogleQuoteProvider()

        results = provider.search(
            "happiness",
            limit=5,
        )

    assert len(results) == 1
    assert results[0].text == (
        "True happiness comes from appreciating what you have."
    )
    assert results[0].source == "Google Search"
    assert results[0].url == "https://example.com/quote"


def test_google_provider_respects_limit():
    html = """
    <html>
        <body>
            <div class="MjjYud">
                <a href="https://example.com/1">
                    <h3>Quote 1</h3>
                </a>
                <div class="VwiC3b">Happiness quote one.</div>
            </div>

            <div class="MjjYud">
                <a href="https://example.com/2">
                    <h3>Quote 2</h3>
                </a>
                <div class="VwiC3b">Happiness quote two.</div>
            </div>

            <div class="MjjYud">
                <a href="https://example.com/3">
                    <h3>Quote 3</h3>
                </a>
                <div class="VwiC3b">Happiness quote three.</div>
            </div>
        </body>
    </html>
    """

    response = Mock()
    response.text = html
    response.raise_for_status.return_value = None

    with patch(
        "app.services.web_search.google_provider.requests.get",
        return_value=response,
    ):
        provider = GoogleQuoteProvider()

        results = provider.search(
            "happiness",
            limit=2,
        )

    assert len(results) == 2


def test_google_provider_empty_query():
    provider = GoogleQuoteProvider()

    assert provider.search("", limit=10) == []


def test_google_provider_handles_request_failure():
    import requests

    with patch(
        "app.services.web_search.google_provider.requests.get",
        side_effect=requests.RequestException,
    ):
        provider = GoogleQuoteProvider()

        assert provider.search(
            "happiness",
            limit=10,
        ) == []
