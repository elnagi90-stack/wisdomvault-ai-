from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.services.book_service import BookService


async def add_book(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    service: BookService = context.bot_data["book_service"]

    if not context.args:
        await update.message.reply_text(
            "استخدم الأمر بالشكل ده:\n/addbook عنوان الكتاب هنا"
        )
        return

    title = " ".join(context.args)

    try:
        book = service.create_book(title=title)
    except ValueError as exc:
        await update.message.reply_text(f"⚠️ {exc}")
        return

    await update.message.reply_text(
        f"✅ اتضاف الكتاب: {book.title}\nID: `{book.id}`",
        parse_mode="Markdown",
    )


async def my_books(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    service: BookService = context.bot_data["book_service"]
    books = service.list_books()

    if not books:
        await update.message.reply_text("لسه معندكش كتب محفوظة.")
        return

    lines = [f"📚 {book.title}  (`{book.id}`)" for book in books]

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
    )
