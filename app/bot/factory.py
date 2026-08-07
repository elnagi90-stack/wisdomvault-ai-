from __future__ import annotations

from telegram.ext import Application, CommandHandler

from app.bot.commands.books import add_book, my_books
from app.bot.commands.quotes import (
    add_quote,
    favorite_quote,
    favorites,
    my_quotes,
    random_quote,
)
from app.core.config import Settings
from app.database.base import create_engine_from_settings
from app.database.session import build_session_factory
from app.services.book_service import BookService
from app.services.quote_service import QuoteService


async def start_command(update, context) -> None:
    await update.message.reply_text(
        "Welcome to WisdomVault AI 📚\n\n"
        "الأوامر المتاحة:\n"
        "/addquote <نص> — إضافة اقتباس\n"
        "/myquotes — آخر الاقتباسات\n"
        "/random — اقتباس عشوائي\n"
        "/favorites — الاقتباسات المفضلة\n"
        "/favorite <id> — إضافة اقتباس للمفضلة\n"
        "/addbook <عنوان> — إضافة كتاب\n"
        "/mybooks — كل الكتب"
    )


def build_bot_application(
    token: str | None = None,
    settings: Settings | None = None,
) -> Application:
    settings = settings or Settings()

    application = (
        Application.builder()
        .token(token or settings.telegram_bot_token or "test-token")
        .build()
    )

    engine = create_engine_from_settings(settings)
    session_factory = build_session_factory(engine)

    application.bot_data["quote_service"] = QuoteService(session_factory=session_factory)
    application.bot_data["book_service"] = BookService(session_factory=session_factory)

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("addquote", add_quote))
    application.add_handler(CommandHandler("myquotes", my_quotes))
    application.add_handler(CommandHandler("random", random_quote))
    application.add_handler(CommandHandler("favorites", favorites))
    application.add_handler(CommandHandler("favorite", favorite_quote))
    application.add_handler(CommandHandler("addbook", add_book))
    application.add_handler(CommandHandler("mybooks", my_books))

    return application


def run_bot() -> None:
    application = build_bot_application()
    application.run_polling()
