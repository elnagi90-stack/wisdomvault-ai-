from app.bot.factory import build_bot_application


def test_build_bot_application_returns_ready_app() -> None:
    app = build_bot_application(token="test-token")
    assert app is not None
