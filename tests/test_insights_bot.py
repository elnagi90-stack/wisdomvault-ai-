from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.bot.commands.insights import summarize_book
from app.bot.factory import build_bot_application


def _make_update_and_context(args: list[str] | None = None):
    update = MagicMock()
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.args = args or []
    context.bot_data = {}

    return update, context


def test_build_bot_application_wires_ai_service() -> None:
    app = build_bot_application(token="test-token")
    assert "ai_service" in app.bot_data


def test_build_bot_application_registers_booksummary_command() -> None:
    app = build_bot_application(token="test-token")

    handler_types = [
        type(h).__name__ for group in app.handlers.values() for h in group
    ]

    assert handler_types.count("CommandHandler") >= 10


@pytest.mark.asyncio
async def test_summarize_book_with_no_args_prompts_usage() -> None:
    update, context = _make_update_and_context(args=[])
    context.bot_data["book_service"] = MagicMock()
    context.bot_data["quote_service"] = MagicMock()
    context.bot_data["ai_service"] = MagicMock()

    await summarize_book(update, context)

    update.message.reply_text.assert_called_once()
    assert "booksummary" in update.message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_summarize_book_reports_missing_book() -> None:
    update, context = _make_update_and_context(args=["some-id"])

    book_service = MagicMock()
    book_service.get_book.return_value = None
    context.bot_data["book_service"] = book_service
    context.bot_data["quote_service"] = MagicMock()
    context.bot_data["ai_service"] = MagicMock()

    await summarize_book(update, context)

    update.message.reply_text.assert_called_once()
    assert "مفيش كتاب" in update.message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_summarize_book_reports_when_no_quotes_saved() -> None:
    update, context = _make_update_and_context(args=["book-1"])

    book = MagicMock()
    book.title = "The Alchemist"

    book_service = MagicMock()
    book_service.get_book.return_value = book
    context.bot_data["book_service"] = book_service

    quote_service = MagicMock()
    quote_service.get_quotes_by_book.return_value = []
    context.bot_data["quote_service"] = quote_service
    context.bot_data["ai_service"] = MagicMock()

    await summarize_book(update, context)

    message = update.message.reply_text.call_args[0][0]
    assert "The Alchemist" in message
    assert "لسه معندكش" in message


@pytest.mark.asyncio
async def test_summarize_book_sends_representative_highlights() -> None:
    update, context = _make_update_and_context(args=["book-1"])

    book = MagicMock()
    book.title = "The Alchemist"

    book_service = MagicMock()
    book_service.get_book.return_value = book
    context.bot_data["book_service"] = book_service

    quote_1 = MagicMock()
    quote_1.text = "Quote one."
    quote_2 = MagicMock()
    quote_2.text = "Quote two."

    quote_service = MagicMock()
    quote_service.get_quotes_by_book.return_value = [quote_1, quote_2]
    context.bot_data["quote_service"] = quote_service

    ai_service = MagicMock()
    ai_service.select_representative.return_value = ["Quote one.", "Quote two."]
    context.bot_data["ai_service"] = ai_service

    await summarize_book(update, context)

    ai_service.select_representative.assert_called_once_with(
        ["Quote one.", "Quote two."],
        max_passages=5,
    )

    message = update.message.reply_text.call_args[0][0]
    assert "The Alchemist" in message
    assert "Quote one." in message
    assert "Quote two." in message
    assert "1." in message and "2." in message
