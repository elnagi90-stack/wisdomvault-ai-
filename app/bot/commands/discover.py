from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.ocr.engine import OcrEngineUnavailableError
from app.schemas.web_search.quote import WebQuoteResult
from app.services.ocr_service import OcrService, UnsupportedImageError
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


async def _search_and_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    query_text: str,
) -> None:
    """Shared by /findsimilar (text) and the photo/OCR flow — same
    search call, same formatting, same Save buttons either way."""
    web_search_service: WebSearchService = context.bot_data["web_search_service"]

    await update.message.reply_text("🔎 بدور على اقتباسات مشابهة...")

    try:
        results = web_search_service.search(query_text, limit=MAX_RESULTS)
    except Exception:
        await update.message.reply_text(
            "⚠️ حصلت مشكلة أثناء البحث، جرّب تاني كمان شوية."
        )
        return

    if not results:
        await update.message.reply_text("معلقتش على أي اقتباسات مشابهة، جرّب صياغة تانية.")
        return

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


async def find_similar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not context.args:
        await update.message.reply_text(
            "استخدم الأمر بالشكل ده:\n/findsimilar نص الاقتباس اللي عايز تلاقي شبهه"
        )
        return

    query = " ".join(context.args)

    await _search_and_reply(update, context, query)


async def handle_quote_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """User sends a photo of a quote (book page, screenshot, etc.):
    OCR extracts the text, then it's fed into the exact same
    discovery pipeline as /findsimilar."""
    ocr_service: OcrService = context.bot_data["ocr_service"]

    photo = update.message.photo[-1]  # highest resolution available
    telegram_file = await photo.get_file()
    image_bytes = bytes(await telegram_file.download_as_bytearray())

    await update.message.reply_text("🖼️ بستخرج النص من الصورة...")

    try:
        text, _saved_path = ocr_service.extract_text_from_image(
            image_bytes,
            content_type="image/jpeg",
        )
    except UnsupportedImageError as exc:
        await update.message.reply_text(f"⚠️ {exc}")
        return
    except OcrEngineUnavailableError:
        await update.message.reply_text(
            "⚠️ خدمة استخراج النص مش شغالة دلوقتي، جرّب تاني بعدين."
        )
        return

    if not text.strip():
        await update.message.reply_text(
            "معرفتش أستخرج نص من الصورة دي، جرّب صورة أوضح."
        )
        return

    await update.message.reply_text(f"📝 النص اللي طلع من الصورة:\n«{text}»")

    await _search_and_reply(update, context, text)


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
