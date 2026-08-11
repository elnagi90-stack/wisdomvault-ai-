from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.schemas.web_search.quote import WebQuoteResult
from app.services.ocr_service import OcrService
from app.services.quote_service import QuoteService
from app.services.web_search.service import WebSearchService

MAX_RESULTS = 5


def _format_result(result: WebQuoteResult, index: int) -> str:
    lines = [
        f"🔎 اقتباس مشابه #{index + 1}",
        "",
        f"«{result.text}»",
    ]

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


async def photo_quote_search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None or update.message.photo is None:
        return

    await update.message.reply_text(
        "📷 استلمت الصورة.\n"
        "🔍 بقرأ الاقتباس منها وببحث عن اقتباسات مشابهة..."
    )

    try:
        photo = update.message.photo[-1]
        telegram_file = await photo.get_file()
        image_bytes = bytes(
            await telegram_file.download_as_bytearray()
        )

        ocr_service: OcrService = context.bot_data["ocr_service"]
        text = ocr_service.extract_text(image_bytes)

    except Exception:
        await update.message.reply_text(
            "⚠️ حصلت مشكلة أثناء قراءة الصورة. "
            "جرّب صورة أوضح."
        )
        return

    if not text.strip():
        await update.message.reply_text(
            "⚠️ مقدرتش أقرأ نص واضح من الصورة.\n"
            "جرّب صورة أوضح أو ابعت الصورة بشكل مستقيم."
        )
        return

    await update.message.reply_text(
        f"📝 النص اللي قرأته:\n\n«{text}»\n\n"
        "🔎 بدور على اقتباسات مشابهة..."
    )

    try:
        web_search_service: WebSearchService = (
            context.bot_data["web_search_service"]
        )

        results = web_search_service.search(
            text,
            limit=MAX_RESULTS,
        )

    except Exception:
        await update.message.reply_text(
            "⚠️ قدرت أقرأ النص، لكن حصلت مشكلة أثناء البحث."
        )
        return

    if not results:
        await update.message.reply_text(
            "معلقتش على اقتباسات مشابهة "
            "من المصادر المتاحة."
        )
        return

    # Save results so the Save buttons can retrieve them.
    pending: dict[str, WebQuoteResult] = {}

    for index, result in enumerate(results):
        pending[str(index)] = result

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "💾 احفظ",
                        callback_data=f"save_web_quote:{index}",
                    )
                ]
            ]
        )

        await update.message.reply_text(
            _format_result(result, index),
            reply_markup=keyboard,
        )

    context.user_data["pending_web_quotes"] = pending
