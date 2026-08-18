from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest

from app.services.ai_service import AiService, _split_sentences


def test_split_sentences_basic() -> None:
    text = "This is one sentence. This is another one! And a third?"
    sentences = _split_sentences(text)

    assert sentences == [
        "This is one sentence.",
        "This is another one!",
        "And a third?",
    ]


def test_split_sentences_drops_very_short_fragments() -> None:
    text = "Ok. This is a real sentence with enough words."
    sentences = _split_sentences(text)

    assert sentences == ["This is a real sentence with enough words."]


def test_split_sentences_empty_input() -> None:
    assert _split_sentences("") == []
    assert _split_sentences("   ") == []


def test_summarize_empty_text_returns_placeholder() -> None:
    service = AiService()
    assert service.summarize("") == "Summary: (no content to summarize)"


def test_summarize_short_text_returns_all_sentences_unchanged() -> None:
    service = AiService()
    text = "First sentence here. Second sentence here."

    result = service.summarize(text, max_sentences=3)

    assert result == "Summary: First sentence here. Second sentence here."


def test_summarize_prefixes_with_summary_label() -> None:
    service = AiService()
    result = service.summarize("This is a long document about memory and learning")
    assert "Summary" in result


def test_summarize_picks_most_central_sentences_and_keeps_reading_order() -> None:
    service = AiService()

    sentences = [
        "Cats are wonderful pets that bring joy every day.",
        "Cars need regular maintenance to keep running well.",
        "Many people love cats for their independent nature.",
        "Cats also make great companions for elderly people.",
    ]
    text = " ".join(sentences)

    vectors = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [0.95, 0.05],
            [0.9, 0.1],
        ],
        dtype="float32",
    )

    with patch(
        "app.ai.embedding_service.EmbeddingService.encode_many",
        return_value=vectors,
    ):
        result = service.summarize(text, max_sentences=2)

    assert result.startswith("Summary: ")
    body = result[len("Summary: "):]

    assert "Cars need regular maintenance" not in body
    assert body.index(sentences[0]) < body.index(sentences[2])


def test_summarize_respects_max_sentences() -> None:
    service = AiService()

    sentences = [f"This is sentence number {i} in the document." for i in range(6)]
    text = " ".join(sentences)

    vectors = np.eye(6, dtype="float32")

    with patch(
        "app.ai.embedding_service.EmbeddingService.encode_many",
        return_value=vectors,
    ):
        result = service.summarize(text, max_sentences=2)

    body = result[len("Summary: "):]
    selected_count = sum(1 for s in sentences if s in body)
    assert selected_count == 2


def test_summarize_falls_back_gracefully_when_embeddings_unavailable() -> None:
    service = AiService()

    sentences = [f"This is sentence number {i} in the document." for i in range(5)]
    text = " ".join(sentences)

    with patch(
        "app.ai.embedding_service.EmbeddingService.encode_many",
        side_effect=RuntimeError("model failed to load"),
    ):
        result = service.summarize(text, max_sentences=2)

    assert result.startswith("Summary: ")
    assert sentences[0] in result
    assert sentences[1] in result


# ---- select_representative (used for per-book quote highlights) ----

def test_select_representative_returns_all_when_under_the_limit() -> None:
    service = AiService()
    passages = ["First quote.", "Second quote."]

    result = service.select_representative(passages, max_passages=5)

    assert result == passages


def test_select_representative_drops_empty_and_blank_passages() -> None:
    service = AiService()
    passages = ["A real quote here.", "", "   ", "Another real quote."]

    result = service.select_representative(passages, max_passages=5)

    assert result == ["A real quote here.", "Another real quote."]


def test_select_representative_picks_central_passages_in_original_order() -> None:
    service = AiService()

    passages = [
        "Cats are wonderful pets that bring joy every day.",
        "Cars need regular maintenance to keep running well.",
        "Many people love cats for their independent nature.",
        "Cats also make great companions for elderly people.",
    ]

    vectors = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [0.95, 0.05],
            [0.9, 0.1],
        ],
        dtype="float32",
    )

    with patch(
        "app.ai.embedding_service.EmbeddingService.encode_many",
        return_value=vectors,
    ):
        result = service.select_representative(passages, max_passages=2)

    assert passages[1] not in result
    assert result.index(passages[0]) < result.index(passages[2])


def test_select_representative_empty_list_returns_empty() -> None:
    service = AiService()
    assert service.select_representative([], max_passages=5) == []
