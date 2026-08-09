from app.schemas.web_search.quote import WebQuoteResult
from app.services.web_search.ranker import WebQuoteRanker


def test_web_quote_ranker_orders_by_semantic_similarity():
    ranker = WebQuoteRanker()

    results = [
        WebQuoteResult(
            text="The weather is beautiful today.",
            source="test",
        ),
        WebQuoteResult(
            text="True happiness comes from appreciating what you already have.",
            source="test",
        ),
        WebQuoteResult(
            text="A person becomes happier when they stop chasing more and value what they possess.",
            source="test",
        ),
    ]

    ranked = ranker.rank(
        query="Happiness comes from appreciating what you have.",
        results=results,
        limit=3,
    )

    assert len(ranked) == 3

    assert ranked[0].score is not None
    assert ranked[1].score is not None
    assert ranked[2].score is not None

    assert (
        ranked[0].score
        >= ranked[1].score
        >= ranked[2].score
    )


def test_web_quote_ranker_respects_limit():
    ranker = WebQuoteRanker()

    results = [
        WebQuoteResult(
            text=f"Happiness quote number {i}",
            source="test",
        )
        for i in range(10)
    ]

    ranked = ranker.rank(
        query="happiness",
        results=results,
        limit=3,
    )

    assert len(ranked) == 3


def test_web_quote_ranker_empty_query():
    ranker = WebQuoteRanker()

    results = [
        WebQuoteResult(
            text="Happiness is real.",
            source="test",
        )
    ]

    ranked = ranker.rank(
        query="",
        results=results,
        limit=10,
    )

    assert ranked == []


def test_web_quote_ranker_empty_results():
    ranker = WebQuoteRanker()

    ranked = ranker.rank(
        query="happiness",
        results=[],
        limit=10,
    )

    assert ranked == []


def test_source_quality_bonus_breaks_near_ties():
    """Two candidates with identical semantic similarity should be
    ordered with the more reputable source first."""
    import numpy as np
    from unittest.mock import patch

    ranker = WebQuoteRanker()

    same_vector = np.array([1.0, 0.0], dtype="float32")

    results = [
        WebQuoteResult(text="Quote from an unknown blog", source="Random Blog"),
        WebQuoteResult(text="Quote from Goodreads", source="Goodreads"),
    ]

    with patch.object(
        ranker.embedding, "encode_one", return_value=same_vector
    ), patch.object(
        ranker.embedding,
        "encode_many",
        return_value=[same_vector, same_vector],
    ):
        ranked = ranker.rank(query="wisdom", results=results, limit=2)

    assert ranked[0].source == "Goodreads"
    assert ranked[1].source == "Random Blog"
    assert ranked[0].score > ranked[1].score


def test_source_quality_bonus_cannot_override_a_real_semantic_gap():
    """A weak semantic match from a reputable source should still lose
    to a strong semantic match from an unknown source — the source
    bonus is a tie-breaker, not a ranking override."""
    import numpy as np
    from unittest.mock import patch

    ranker = WebQuoteRanker()

    strong_match = np.array([1.0, 0.0], dtype="float32")
    weak_match = np.array([0.5, 0.5], dtype="float32")  # lower dot product

    results = [
        WebQuoteResult(text="Weak match but from Goodreads", source="Goodreads"),
        WebQuoteResult(text="Strong match, unknown source", source="Random Blog"),
    ]

    with patch.object(
        ranker.embedding, "encode_one", return_value=strong_match
    ), patch.object(
        ranker.embedding,
        "encode_many",
        return_value=[weak_match, strong_match],
    ):
        ranked = ranker.rank(query="wisdom", results=results, limit=2)

    assert ranked[0].source == "Random Blog"
    assert ranked[1].source == "Goodreads"


def test_unknown_source_gets_no_bonus():
    ranker = WebQuoteRanker()
    assert ranker._source_bonus("Some Random Website") == 0.0
    assert ranker._source_bonus(None) == 0.0
    assert ranker._source_bonus("Goodreads") == 0.05
    assert ranker._source_bonus("goodreads") == 0.05  # case-insensitive
