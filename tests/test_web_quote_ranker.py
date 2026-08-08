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
