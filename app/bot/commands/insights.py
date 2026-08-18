from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.services.ai_service import AiService
from app.services.book_service import BookService
from app.services.quote_service import QuoteService

MAX_HIGHLIGHTS = 5


async def summarize_book(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """/booksummary <book_id> -- picks the most representative quotes
    the user has saved from a book, as a quick "highlights" summary.

    This doesn't need the book's full text (which the app never has) --
    it works entirely from the user's own captured quotes, using the
    same free/local centrality scoring as AiService.summarize().
    """
    book_service: BookService = context.bot_data["book_service"]
    quote_service: QuoteService = context.bot_data["quote_service"]
    ai_service: AiService = context.bot_data["ai_service"]

    if not context.args:
        await update.message.reply_text(
            "استخدم الأمر بالشكل ده:\n/booksummary ID_الكتاب\n\n"
            "(هتلاقي الـ ID من أمر /mybooks)"
        )
        return

    book_id = context.args[0]
    book = book_service.get_book(book_id)

    if book is None:
        await update.message.reply_text("مفيش كتاب بالـ ID ده.")
        return

    quotes = quote_service.get_quotes_by_book(book_id)

    if not quotes:
        await update.message.reply_text(
            f"لسه معندكش اقتباسات محفوظة من «{book.title}»."
        )
        return

    highlights = ai_service.select_representative(
        [quote.text for quote in quotes],
        max_passages=MAX_HIGHLIGHTS,
    )

    lines = [f"📚 أهم اقتباساتك من «{book.title}»:", ""]

    for index, text in enumerate(highlights, start=1):
        lines.append(f"{index}. «{text}»")

    await update.message.reply_text("\n".join(lines))
