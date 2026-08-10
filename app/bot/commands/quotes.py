from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.services.quote_service import QuoteService


def _format_quote(quote) -> str:
    lines = [f"📖 {quote.text}"]

    if quote.book is not None:
        lines.append(f"— {quote.book.title}")

    lines.append(f"\nID: `{quote.id}`")

    return "\n".join(lines)


async def add_quote(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    service: QuoteService = context.bot_data["quote_service"]

    if not context.args:
        await update.message.reply_text(
            "استخدم الأمر بالشكل ده:\n/addquote نص الاقتباس هنا"
        )
        return

    text = " ".join(context.args)

    try:
        quote = service.create_quote(text=text)
    except ValueError as exc:
        await update.message.reply_text(f"⚠️ {exc}")
        return

    await update.message.reply_text(
        f"✅ اتضاف الاقتباس.\nID: `{quote.id}`",
        parse_mode="Markdown",
    )


async def my_quotes(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    service: QuoteService = context.bot_data["quote_service"]
    quotes = service.list_quotes(limit=10)

    if not quotes:
        await update.message.reply_text("لسه معندكش اقتباسات محفوظة.")
        return

    for quote in quotes:
        await update.message.reply_text(
            _format_quote(quote),
            parse_mode="Markdown",
        )


async def random_quote(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    service: QuoteService = context.bot_data["quote_service"]
    quote = service.get_random_quote()

    if quote is None:
        await update.message.reply_text("لسه معندكش اقتباسات محفوظة.")
        return

    await update.message.reply_text(
        _format_quote(quote),
        parse_mode="Markdown",
    )


async def favorites(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    service: QuoteService = context.bot_data["quote_service"]
    quotes = service.get_favorites()

    if not quotes:
        await update.message.reply_text("لسه معندكش اقتباسات مفضلة.")
        return

    for quote in quotes:
        await update.message.reply_text(
            _format_quote(quote),
            parse_mode="Markdown",
        )


async def favorite_quote(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    service: QuoteService = context.bot_data["quote_service"]

    if not context.args:
        await update.message.reply_text(
            "استخدم الأمر بالشكل ده:\n/favorite ID_الاقتباس"
        )
        return

    quote_id = context.args[0]
    quote = service.set_favorite(quote_id, True)

    if quote is None:
        await update.message.reply_text("مفيش اقتباس بالـ ID ده.")
        return

    await update.message.reply_text("⭐ اتحط في المفضلة.")
