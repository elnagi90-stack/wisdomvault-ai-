from __future__ import annotations

from unittest.mock import Mock, patch

import requests

from app.services.web_search.page_extractor import WebPageExtractor


def make_response(html: str, status_code: int = 200) -> Mock:
    response = Mock()
    response.text = html
    response.status_code = status_code

    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(
            f"HTTP {status_code}"
        )
    else:
        response.raise_for_status.return_value = None

    return response


def test_extract_rejects_empty_url() -> None:
    extractor = WebPageExtractor()

    assert extractor.extract("") == ""


def test_extract_rejects_invalid_url() -> None:
    extractor = WebPageExtractor()

    assert extractor.extract("not-a-url") == ""


def test_extract_rejects_unsupported_scheme() -> None:
    extractor = WebPageExtractor()

    assert extractor.extract("ftp://example.com/page") == ""


def test_extract_rejects_invalid_max_chars() -> None:
    extractor = WebPageExtractor()

    assert extractor.extract(
        "https://example.com",
        max_chars=0,
    ) == ""


@patch("app.services.web_search.page_extractor.requests.get")
def test_extract_returns_empty_on_request_failure(
    mock_get: Mock,
) -> None:
    mock_get.side_effect = requests.RequestException(
        "connection failed"
    )

    extractor = WebPageExtractor()

    assert extractor.extract(
        "https://example.com"
    ) == ""


@patch("app.services.web_search.page_extractor.requests.get")
def test_extract_removes_unwanted_elements(
    mock_get: Mock,
) -> None:
    html = """
    <html>
        <body>
            <nav>Navigation</nav>
            <header>Header</header>
            <main>
                <p>This is useful content.</p>
                <script>alert("bad")</script>
                <style>.bad { color: red; }</style>
                <footer>Footer</footer>
            </main>
        </body>
    </html>
    """

    mock_get.return_value = make_response(html)

    extractor = WebPageExtractor()

    result = extractor.extract(
        "https://example.com"
    )

    assert "This is useful content." in result
    assert "Navigation" not in result
    assert "Header" not in result
    assert "Footer" not in result
    assert "alert" not in result
    assert "color: red" not in result


@patch("app.services.web_search.page_extractor.requests.get")
def test_extract_prefers_article(
    mock_get: Mock,
) -> None:
    html = """
    <html>
        <body>
            <main>Wrong main content.</main>
            <article>
                <p>The real article content.</p>
            </article>
        </body>
    </html>
    """

    mock_get.return_value = make_response(html)

    extractor = WebPageExtractor()

    result = extractor.extract(
        "https://example.com/article"
    )

    assert result == "The real article content."


@patch("app.services.web_search.page_extractor.requests.get")
def test_extract_uses_main_when_article_is_missing(
    mock_get: Mock,
) -> None:
    html = """
    <html>
        <body>
            <div>Other content.</div>
            <main>
                <p>The main content.</p>
            </main>
        </body>
    </html>
    """

    mock_get.return_value = make_response(html)

    extractor = WebPageExtractor()

    result = extractor.extract(
        "https://example.com/main"
    )

    assert result == "The main content."


@patch("app.services.web_search.page_extractor.requests.get")
def test_extract_falls_back_to_body(
    mock_get: Mock,
) -> None:
    html = """
    <html>
        <body>
            <p>Body content only.</p>
        </body>
    </html>
    """

    mock_get.return_value = make_response(html)

    extractor = WebPageExtractor()

    result = extractor.extract(
        "https://example.com/body"
    )

    assert result == "Body content only."


@patch("app.services.web_search.page_extractor.requests.get")
def test_extract_normalizes_whitespace(
    mock_get: Mock,
) -> None:
    html = """
    <article>
        <p>
            First    part
            of the text.
        </p>
        <p>
            Second
            part.
        </p>
    </article>
    """

    mock_get.return_value = make_response(html)

    extractor = WebPageExtractor()

    result = extractor.extract(
        "https://example.com/whitespace"
    )

    assert result == "First part of the text. Second part."


@patch("app.services.web_search.page_extractor.requests.get")
def test_extract_respects_max_chars(
    mock_get: Mock,
) -> None:
    html = """
    <article>
        <p>
            This is a deliberately long piece of content
            that should be truncated by the extractor.
        </p>
    </article>
    """

    mock_get.return_value = make_response(html)

    extractor = WebPageExtractor()

    result = extractor.extract(
        "https://example.com/long",
        max_chars=30,
    )

    assert len(result) <= 30
