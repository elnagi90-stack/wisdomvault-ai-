from __future__ import annotations

from app.services.web_search.quote_extractor import QuoteExtractor


def test_extract_from_html_blockquote() -> None:
    extractor = QuoteExtractor()

    html = """
    <html>
        <body>
            <blockquote>
                The only way to do great work is to love what you do.
            </blockquote>
        </body>
    </html>
    """

    results = extractor.extract_html(html)

    assert (
        "The only way to do great work is to love what you do."
        in results
    )


def test_extract_html_finds_multiple_blockquotes() -> None:
    extractor = QuoteExtractor()

    html = """
    <blockquote>First meaningful quotation here.</blockquote>
    <p>Some unrelated page text.</p>
    <blockquote>Second meaningful quotation here.</blockquote>
    """

    results = extractor.extract_html(html)

    assert "First meaningful quotation here." in results
    assert "Second meaningful quotation here." in results


def test_extract_html_ignores_short_blockquotes() -> None:
    extractor = QuoteExtractor()

    html = """
    <blockquote>Hi.</blockquote>
    <blockquote>This is a meaningful quotation.</blockquote>
    """

    results = extractor.extract_html(html)

    assert "Hi." not in results
    assert "This is a meaningful quotation." in results


def test_extract_html_removes_duplicate_blockquotes() -> None:
    extractor = QuoteExtractor()

    html = """
    <blockquote>The same quotation appears twice.</blockquote>
    <blockquote>The same quotation appears twice.</blockquote>
    """

    results = extractor.extract_html(html)

    assert results.count(
        "The same quotation appears twice."
    ) == 1


def test_extract_html_respects_limit() -> None:
    extractor = QuoteExtractor()

    html = """
    <blockquote>First meaningful quotation here.</blockquote>
    <blockquote>Second meaningful quotation here.</blockquote>
    <blockquote>Third meaningful quotation here.</blockquote>
    """

    results = extractor.extract_html(
        html,
        limit=2,
    )

    assert len(results) == 2
