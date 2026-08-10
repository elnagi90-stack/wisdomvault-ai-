from __future__ import annotations

from app.services.web_search.quote_validator import QuoteValidator


def test_validator_accepts_normal_quote() -> None:
    validator = QuoteValidator()

    assert validator.is_valid(
        "The important thing is to never stop learning."
    )


def test_validator_rejects_truncated_quote() -> None:
    validator = QuoteValidator()

    assert not validator.is_valid(
        "The important thing is to keep learning..."
    )


def test_validator_rejects_broken_start() -> None:
    validator = QuoteValidator()

    assert not validator.is_valid(
        "re gone and you will keep going forward always asking for more"
    )


def test_validator_rejects_dangling_attribution_separator() -> None:
    validator = QuoteValidator()

    assert not validator.is_valid(
        "Each of our mistakes makes us stronger. "
        "They are our life lessons. They make us grow. "
        "And I think that is the most important thing in life. "
        "To keep making mistakes and learning from them, "
        "so that we never stop growing.” ―"
    )


def test_validator_rejects_dangling_em_dash() -> None:
    validator = QuoteValidator()

    assert not validator.is_valid(
        "This is a meaningful quote about learning ―"
    )


def test_validator_accepts_quote_with_normal_punctuation() -> None:
    validator = QuoteValidator()

    assert validator.is_valid(
        "Learning never stops, and wisdom grows with experience."
    )
