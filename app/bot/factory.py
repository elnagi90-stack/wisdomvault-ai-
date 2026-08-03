from __future__ import annotations

from telegram.ext import Application, CommandHandler


async def start_command(update, context) -> None:
    await update.message.reply_text("Welcome to WisdomVault AI")


def build_bot_application(token: str | None = None) -> Application:
    application = Application.builder().token(token or "test-token").build()
    application.add_handler(CommandHandler("start", start_command))
    return application
