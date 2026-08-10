from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.schemas.web_search.quote import WebQuoteResult
from app.services.quote_service import QuoteService
from app.services.web_search.service import WebSearchService

MAX_RESULTS = 5


def _format_result(result: WebQuoteResult, index: int) -> str:
    lines = [f"🔎 اقتباس مشابه #{index + 1}", "", f"«{result.text}»"]

    if result.author:
        lines.append(f"👤 {result.author}")

    if result.book:
        lines.append(f"📚 {result.book}")

    if result.score is not None:
        similarity_percent = round(result.score * 100)
        lines.append(f"⭐ التشابه: {similarity_percent}%")

    if result.source:
        lines.append(f"\nالمصدر: {result.source}")

    return "\n".join(lines)


async def find_similar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    web_search_service: WebSearchService = context.bot_data["web_search_service"]

    if not context.args:
        await update.message.reply_text(
            "استخدم الأمر بالشكل ده:\n/findsimilar نص الاقتباس اللي عايز تلاقي شبهه"
        )
        return

    query = " ".join(context.args)

    await update.message.reply_text("🔎 بدور على اقتباسات مشابهة...")

    try:
        results = web_search_service.search(query, limit=MAX_RESULTS)
    except Exception:
        await update.message.reply_text(
            "⚠️ حصلت مشكلة أثناء البحث، جرّب تاني كمان شوية."
        )
        return

    if not results:
        await update.message.reply_text("معلقتش على أي اقتباسات مشابهة، جرّب صياغة تانية.")
        return

    # Stash the actual result objects in this chat's user_data so the
    # "Save" button callback can look them up later — Telegram's
    # callback_data has a tight byte limit, so we only send an index.
    pending: dict[str, WebQuoteResult] = {}

    for index, result in enumerate(results):
        pending[str(index)] = result

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("💾 احفظ", callback_data=f"save_web_quote:{index}")]]
        )

        await update.message.reply_text(
            _format_result(result, index),
            reply_markup=keyboard,
        )

    context.user_data["pending_web_quotes"] = pending


async def save_web_quote_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    await query.answer()

    pending: dict[str, WebQuoteResult] = context.user_data.get(
        "pending_web_quotes", {}
    )

    _, _, index = query.data.partition(":")
    result = pending.get(index)

    if result is None:
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            "⚠️ النتيجة دي مش متاحة دلوقتي (ممكن تكون قديمة)، جرّب /findsimilar تاني."
        )
        return

    quote_service: QuoteService = context.bot_data["quote_service"]

    notes = None
    if result.source or result.url:
        notes = f"Imported from {result.source or 'web'}: {result.url or ''}".strip()

    try:
        quote_service.create_quote(text=result.text, notes=notes)
    except ValueError as exc:
        await query.message.reply_text(f"⚠️ {exc}")
        return

    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text("✅ اتحفظ في مكتبتك.")
