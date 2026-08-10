import pytest

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


# ---- semantic similarity threshold ----

def test_case_a_above_threshold_with_no_bonus_is_accepted():
    import numpy as np
    from unittest.mock import patch

    ranker = WebQuoteRanker(min_similarity=0.65)

    query_vec = np.array([1.0, 0.0], dtype="float32")
    # dot product = 0.70
    quote_vec = np.array([0.70, 0.7141], dtype="float32")

    result = WebQuoteResult(text="Some quote", source="Unknown Blog")

    with patch.object(
        ranker.embedding, "encode_one", return_value=query_vec
    ), patch.object(
        ranker.embedding, "encode_many", return_value=[quote_vec]
    ):
        ranked = ranker.rank(query="wisdom", results=[result], limit=5)

    assert len(ranked) == 1
    assert ranked[0].score == pytest.approx(0.70, abs=0.01)


def test_case_b_source_bonus_cannot_rescue_a_below_threshold_candidate():
    """semantic=0.60, bonus=0.05 -> combined=0.65, but the threshold
    must be checked against the RAW 0.60, not the combined 0.65."""
    import numpy as np
    from unittest.mock import patch

    ranker = WebQuoteRanker(min_similarity=0.65)

    query_vec = np.array([1.0, 0.0], dtype="float32")
    quote_vec = np.array([0.60, 0.8], dtype="float32")

    result = WebQuoteResult(text="Weak match", source="Goodreads")

    with patch.object(
        ranker.embedding, "encode_one", return_value=query_vec
    ), patch.object(
        ranker.embedding, "encode_many", return_value=[quote_vec]
    ):
        ranked = ranker.rank(query="wisdom", results=[result], limit=5)

    assert ranked == []


def test_case_c_candidate_above_threshold_still_gets_source_bonus():
    import numpy as np
    from unittest.mock import patch

    ranker = WebQuoteRanker(min_similarity=0.65)

    query_vec = np.array([1.0, 0.0], dtype="float32")
    quote_vec = np.array([0.70, 0.7141], dtype="float32")

    result = WebQuoteResult(text="Good match", source="Goodreads")

    with patch.object(
        ranker.embedding, "encode_one", return_value=query_vec
    ), patch.object(
        ranker.embedding, "encode_many", return_value=[quote_vec]
    ):
        ranked = ranker.rank(query="wisdom", results=[result], limit=5)

    assert len(ranked) == 1
    assert ranked[0].score == pytest.approx(0.75, abs=0.01)  # 0.70 + 0.05


def test_case_d_all_candidates_below_threshold_returns_empty():
    import numpy as np
    from unittest.mock import patch

    ranker = WebQuoteRanker(min_similarity=0.65)

    query_vec = np.array([1.0, 0.0], dtype="float32")
    weak_vec_1 = np.array([0.3, 0.9], dtype="float32")
    weak_vec_2 = np.array([0.2, 0.9], dtype="float32")

    results = [
        WebQuoteResult(text="Irrelevant one", source="Goodreads"),
        WebQuoteResult(text="Irrelevant two", source="Tavily Search"),
    ]

    with patch.object(
        ranker.embedding, "encode_one", return_value=query_vec
    ), patch.object(
        ranker.embedding,
        "encode_many",
        return_value=[weak_vec_1, weak_vec_2],
    ):
        ranked = ranker.rank(query="wisdom", results=results, limit=5)

    assert ranked == []


def test_default_min_similarity_comes_from_settings():
    from app.core.config import settings as app_settings

    ranker = WebQuoteRanker()
    assert ranker.min_similarity == app_settings.min_semantic_similarity


def test_explicit_min_similarity_overrides_settings():
    ranker = WebQuoteRanker(min_similarity=0.9)
    assert ranker.min_similarity == 0.9
