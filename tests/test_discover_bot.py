from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.bot.commands.discover import find_similar, save_web_quote_callback
from app.bot.factory import build_bot_application
from app.schemas.web_search.quote import WebQuoteResult


def _make_update_and_context(args: list[str] | None = None):
    update = MagicMock()
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.args = args or []
    context.user_data = {}
    context.bot_data = {}

    return update, context


# ---- bot wiring ----

def test_build_bot_application_wires_web_search_service() -> None:
    app = build_bot_application(token="test-token")
    assert "web_search_service" in app.bot_data


def test_build_bot_application_registers_findsimilar_and_callback() -> None:
    app = build_bot_application(token="test-token")

    handler_types = [
        type(h).__name__ for group in app.handlers.values() for h in group
    ]

    assert handler_types.count("CommandHandler") >= 9
    assert "CallbackQueryHandler" in handler_types


# ---- /findsimilar command ----

@pytest.mark.asyncio
async def test_find_similar_with_no_args_prompts_usage() -> None:
    update, context = _make_update_and_context(args=[])
    context.bot_data["web_search_service"] = MagicMock()

    await find_similar(update, context)

    update.message.reply_text.assert_called_once()
    assert "findsimilar" in update.message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_find_similar_reports_when_nothing_found() -> None:
    update, context = _make_update_and_context(args=["some", "quote"])
    web_search_service = MagicMock()
    web_search_service.search.return_value = []
    context.bot_data["web_search_service"] = web_search_service

    await find_similar(update, context)

    messages = [call.args[0] for call in update.message.reply_text.call_args_list]
    assert any("مشابه" in m for m in messages)


@pytest.mark.asyncio
async def test_find_similar_sends_each_result_and_stores_pending() -> None:
    update, context = _make_update_and_context(args=["wisdom"])
    web_search_service = MagicMock()
    web_search_service.search.return_value = [
        WebQuoteResult(
            text="Knowledge speaks, wisdom listens",
            author="Jimi Hendrix",
            source="Goodreads",
            score=0.87,
        ),
        WebQuoteResult(
            text="An investment in knowledge pays the best interest",
            author="Benjamin Franklin",
            source="Goodreads",
            score=0.81,
        ),
    ]
    context.bot_data["web_search_service"] = web_search_service

    await find_similar(update, context)

    # 1 "searching..." message + 2 result messages
    assert update.message.reply_text.call_count == 3

    pending = context.user_data["pending_web_quotes"]
    assert set(pending.keys()) == {"0", "1"}
    assert pending["0"].author == "Jimi Hendrix"


@pytest.mark.asyncio
async def test_find_similar_handles_search_errors_gracefully() -> None:
    update, context = _make_update_and_context(args=["wisdom"])
    web_search_service = MagicMock()
    web_search_service.search.side_effect = RuntimeError("boom")
    context.bot_data["web_search_service"] = web_search_service

    await find_similar(update, context)

    messages = [call.args[0] for call in update.message.reply_text.call_args_list]
    assert any("مشكلة" in m for m in messages)


# ---- save button callback ----

def _make_callback_update_and_context(data: str, pending: dict):
    query = MagicMock()
    query.data = data
    query.answer = AsyncMock()
    query.edit_message_reply_markup = AsyncMock()
    query.message.reply_text = AsyncMock()

    update = MagicMock()
    update.callback_query = query

    context = MagicMock()
    context.user_data = {"pending_web_quotes": pending}
    context.bot_data = {}

    return update, context, query


@pytest.mark.asyncio
async def test_save_web_quote_callback_saves_and_confirms() -> None:
    result = WebQuoteResult(
        text="Knowledge speaks, wisdom listens",
        author="Jimi Hendrix",
        source="Goodreads",
        url="https://goodreads.com/x",
    )
    update, context, query = _make_callback_update_and_context(
        "save_web_quote:0", {"0": result}
    )

    quote_service = MagicMock()
    quote_service.create_quote.return_value = MagicMock(id="new-id")
    context.bot_data["quote_service"] = quote_service

    await save_web_quote_callback(update, context)

    quote_service.create_quote.assert_called_once()
    call_kwargs = quote_service.create_quote.call_args.kwargs
    assert call_kwargs["text"] == "Knowledge speaks, wisdom listens"
    assert "Goodreads" in call_kwargs["notes"]

    query.edit_message_reply_markup.assert_called_once_with(reply_markup=None)
    query.message.reply_text.assert_called_once()
    assert "اتحفظ" in query.message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_save_web_quote_callback_handles_missing_pending_result() -> None:
    update, context, query = _make_callback_update_and_context(
        "save_web_quote:5", {}
    )
    context.bot_data["quote_service"] = MagicMock()

    await save_web_quote_callback(update, context)

    query.message.reply_text.assert_called_once()
    assert "مش متاحة" in query.message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_save_web_quote_callback_surfaces_validation_errors() -> None:
    result = WebQuoteResult(text="Some quote", source="Goodreads")
    update, context, query = _make_callback_update_and_context(
        "save_web_quote:0", {"0": result}
    )

    quote_service = MagicMock()
    quote_service.create_quote.side_effect = ValueError("Quote text cannot be empty.")
    context.bot_data["quote_service"] = quote_service

    await save_web_quote_callback(update, context)

    query.message.reply_text.assert_called_once()
    assert "Quote text cannot be empty" in query.message.reply_text.call_args[0][0]
