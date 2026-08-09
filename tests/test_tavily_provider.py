from __future__ import annotations

from unittest.mock import Mock, patch

from app.schemas.web_search.quote import WebQuoteResult
from app.services.web_search.tavily_provider import TavilyQuoteProvider


def test_tavily_returns_empty_without_api_key() -> None:
    provider = TavilyQuoteProvider()

    with patch.dict("os.environ", {}, clear=True):
        provider = TavilyQuoteProvider()
        assert provider.search("wisdom", 5) == []


def test_tavily_reads_api_key_from_settings_by_default() -> None:
    """A real regression guard: earlier the constructor hardcoded
    self.api_key = "" and never consulted config/settings at all, so
    the provider silently returned [] in production even when a real
    Tavily key was configured in the environment."""
    from app.core.config import Settings

    with patch(
        "app.services.web_search.tavily_provider.settings",
        Settings(tavily_api_key="configured-key", _env_file=None),
    ):
        provider = TavilyQuoteProvider()
        assert provider.api_key == "configured-key"


def test_tavily_constructor_accepts_explicit_api_key_override() -> None:
    provider = TavilyQuoteProvider(api_key="explicit-key")
    assert provider.api_key == "explicit-key"


def test_tavily_returns_empty_for_invalid_input() -> None:
    provider = TavilyQuoteProvider()

    assert provider.search("", 5) == []
    assert provider.search("wisdom", 0) == []


def test_tavily_normalizes_results() -> None:
    provider = TavilyQuoteProvider()
    provider.api_key = "test-key"

    fake_response = {
        "results": [
            {
                "title": "The Alchemist Quotes",
                "content": "The important thing is to never stop learning.",
                "url": "https://example.com/alchemist",
            },
            {
                "title": "Wisdom Quotes",
                "content": "Knowledge speaks, wisdom listens.",
                "url": "https://example.com/wisdom",
            },
        ]
    }

    fake_client = Mock()
    fake_client.search.return_value = fake_response

    with patch(
        "app.services.web_search.tavily_provider.TavilyClient",
        return_value=fake_client,
    ):
        results = provider.search(
            "The Alchemist Paulo Coelho quotes",
            5,
        )

    assert len(results) == 2

    assert isinstance(results[0], WebQuoteResult)
    assert (
        results[0].text
        == "The important thing is to never stop learning."
    )
    assert results[0].source == "Tavily Search"
    assert (
        results[0].url
        == "https://example.com/alchemist"
    )


def test_tavily_respects_limit() -> None:
    provider = TavilyQuoteProvider()
    provider.api_key = "test-key"

    fake_response = {
        "results": [
            {
                "content": "Quote one",
                "url": "https://example.com/1",
            },
            {
                "content": "Quote two",
                "url": "https://example.com/2",
            },
            {
                "content": "Quote three",
                "url": "https://example.com/3",
            },
        ]
    }

    fake_client = Mock()
    fake_client.search.return_value = fake_response

    with patch(
        "app.services.web_search.tavily_provider.TavilyClient",
        return_value=fake_client,
    ):
        results = provider.search("wisdom", 2)

    assert len(results) == 2
    fake_client.search.assert_called_once()


def test_tavily_skips_invalid_results() -> None:
    provider = TavilyQuoteProvider()
    provider.api_key = "test-key"

    fake_response = {
        "results": [
            {
                "content": "",
                "url": "https://example.com/empty",
            },
            {
                "content": "Valid quote",
                "url": "",
            },
            {
                "content": "Another valid quote",
                "url": "https://example.com/valid",
            },
        ]
    }

    fake_client = Mock()
    fake_client.search.return_value = fake_response

    with patch(
        "app.services.web_search.tavily_provider.TavilyClient",
        return_value=fake_client,
    ):
        results = provider.search("wisdom", 5)

    assert len(results) == 1
    assert results[0].text == "Another valid quote"


def test_tavily_handles_client_failure() -> None:
    provider = TavilyQuoteProvider()
    provider.api_key = "test-key"

    fake_client = Mock()
    fake_client.search.side_effect = RuntimeError("network failure")

    with patch(
        "app.services.web_search.tavily_provider.TavilyClient",
        return_value=fake_client,
    ):
        assert provider.search("wisdom", 5) == []
