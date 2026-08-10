from __future__ import annotations

from app.services.web_search.metadata.extractor import PageMetadataExtractor


def test_extracts_title() -> None:
    extractor = PageMetadataExtractor()

    html = """
    <html>
        <head>
            <title>The Alchemist Quotes</title>
        </head>
        <body></body>
    </html>
    """

    result = extractor.extract(html)

    assert result.title == "The Alchemist Quotes"


def test_extracts_og_title() -> None:
    extractor = PageMetadataExtractor()

    html = """
    <html>
        <head>
            <meta property="og:title" content="The Alchemist Quotes">
        </head>
    </html>
    """

    result = extractor.extract(html)

    assert result.title == "The Alchemist Quotes"


def test_og_title_is_preferred_over_html_title() -> None:
    extractor = PageMetadataExtractor()

    html = """
    <html>
        <head>
            <title>Generic Page Title</title>
            <meta property="og:title" content="The Alchemist Quotes">
        </head>
    </html>
    """

    result = extractor.extract(html)

    assert result.title == "The Alchemist Quotes"


def test_extracts_author_from_meta() -> None:
    extractor = PageMetadataExtractor()

    html = """
    <html>
        <head>
            <meta name="author" content="Paulo Coelho">
        </head>
    </html>
    """

    result = extractor.extract(html)

    assert result.author == "Paulo Coelho"


def test_extracts_author_from_article_meta() -> None:
    extractor = PageMetadataExtractor()

    html = """
    <html>
        <head></head>
        <body>
            <article>
                <meta name="author" content="Paulo Coelho">
            </article>
        </body>
    </html>
    """

    result = extractor.extract(html)

    assert result.author == "Paulo Coelho"


def test_extracts_book_from_book_title_meta() -> None:
    extractor = PageMetadataExtractor()

    html = """
    <html>
        <head>
            <meta name="book" content="The Alchemist">
        </head>
    </html>
    """

    result = extractor.extract(html)

    assert result.book == "The Alchemist"


def test_extracts_empty_metadata_from_empty_html() -> None:
    extractor = PageMetadataExtractor()

    result = extractor.extract("")

    assert result.title is None
    assert result.author is None
    assert result.book is None


def test_metadata_values_are_trimmed() -> None:
    extractor = PageMetadataExtractor()

    html = """
    <html>
        <head>
            <meta name="author" content="  Paulo Coelho  ">
            <meta name="book" content="  The Alchemist  ">
        </head>
    </html>
    """

    result = extractor.extract(html)

    assert result.author == "Paulo Coelho"
    assert result.book == "The Alchemist"