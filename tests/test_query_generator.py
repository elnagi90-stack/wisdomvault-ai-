from __future__ import annotations

from app.services.web_search.query_generator import (
    MAX_QUERIES,
    QueryGenerator,
)


def test_empty_input_returns_no_queries() -> None:
    generator = QueryGenerator()
    assert generator.generate("") == []
    assert generator.generate("   ") == []
    assert generator.generate(None or "") == []


def test_whitespace_is_normalized() -> None:
    generator = QueryGenerator()

    messy = "  The   important  thing\n\nis to   never stop learning  "
    tidy = "The important thing is to never stop learning"

    assert generator.generate(messy) == generator.generate(tidy)


def test_no_duplicate_queries() -> None:
    generator = QueryGenerator()

    queries = generator.generate("Knowledge is power")

    lowered = [q.lower() for q in queries]
    assert len(lowered) == len(set(lowered))


def test_preserves_the_original_quote_as_an_exact_phrase_query() -> None:
    generator = QueryGenerator()

    quote = "The important thing is to never stop learning"
    queries = generator.generate(quote)

    assert f'"{quote}" quote' in queries


def test_output_is_deterministic() -> None:
    generator = QueryGenerator()

    quote = "The important thing is to never stop learning"

    first_call = generator.generate(quote)
    second_call = generator.generate(quote)

    assert first_call == second_call


def test_respects_maximum_query_count() -> None:
    generator = QueryGenerator()

    long_quote = " ".join([f"word{i}" for i in range(50)])
    queries = generator.generate(long_quote)

    assert len(queries) <= MAX_QUERIES
    assert len(queries) >= 1


def test_generates_multiple_distinct_queries_for_a_normal_quote() -> None:
    generator = QueryGenerator()

    queries = generator.generate(
        "The important thing is to never stop learning"
    )

    assert len(queries) >= 2


def test_single_word_input_still_returns_at_least_one_query() -> None:
    generator = QueryGenerator()
    queries = generator.generate("Wisdom")

    assert queries == ['"Wisdom" quote']


def test_generated_queries_are_never_absurdly_long() -> None:
    generator = QueryGenerator()

    long_quote = " ".join([f"meaningfulword{i}" for i in range(30)])
    queries = generator.generate(long_quote)

    for query in queries:
        assert len(query.split()) <= 14  # a couple words of wrapper quoting/suffix
