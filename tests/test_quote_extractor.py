from __future__ import annotations

from app.services.web_search.quote_extractor import QuoteExtractor


def test_extract_returns_empty_for_empty_text() -> None:
    extractor = QuoteExtractor()

    assert extractor.extract("") == []


def test_extract_returns_empty_for_whitespace() -> None:
    extractor = QuoteExtractor()

    assert extractor.extract("   ") == []


def test_extract_finds_quoted_text() -> None:
    extractor = QuoteExtractor()

    text = (
        'The author wrote, "The only way out is through." '
        "The surrounding text is not a quote."
    )

    results = extractor.extract(text)

    assert "The only way out is through." in results


def test_extract_finds_single_quoted_text() -> None:
    extractor = QuoteExtractor()

    text = "The writer said, 'Knowledge is power.'"

    results = extractor.extract(text)

    assert "Knowledge is power." in results


def test_extract_finds_multiple_quotes() -> None:
    extractor = QuoteExtractor()

    text = (
        '"First meaningful quote." '
        'Some text. '
        '"Second meaningful quote."'
    )

    results = extractor.extract(text)

    assert "First meaningful quote." in results
    assert "Second meaningful quote." in results


def test_extract_removes_duplicate_quotes() -> None:
    extractor = QuoteExtractor()

    text = (
        '"The same quote appears twice." '
        'More text. '
        '"The same quote appears twice."'
    )

    results = extractor.extract(text)

    assert results.count("The same quote appears twice.") == 1


def test_extract_ignores_very_short_quotes() -> None:
    extractor = QuoteExtractor()

    text = (
        '"Hi." '
        '"This is a meaningful quotation."'
    )

    results = extractor.extract(text)

    assert "Hi." not in results
    assert "This is a meaningful quotation." in results


def test_extract_ignores_very_long_quotes() -> None:
    extractor = QuoteExtractor()

    long_quote = " ".join(["word"] * 100)

    text = f'"{long_quote}"'

    results = extractor.extract(text)

    assert results == []


def test_extract_normalizes_whitespace_inside_quotes() -> None:
    extractor = QuoteExtractor()

    text = '"This    quote   has   extra    spaces."'

    results = extractor.extract(text)

    assert "This quote has extra spaces." in results


def test_extract_respects_limit() -> None:
    extractor = QuoteExtractor()

    text = (
        '"First meaningful quote." '
        '"Second meaningful quote." '
        '"Third meaningful quote."'
    )

    results = extractor.extract(
        text,
        limit=2,
    )

    assert len(results) == 2


def test_extract_rejects_invalid_limit() -> None:
    extractor = QuoteExtractor()

    text = '"This is a meaningful quote."'

    assert extractor.extract(
        text,
        limit=0,
    ) == []
