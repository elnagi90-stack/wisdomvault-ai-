from app.core.config import Settings


def test_settings_loads_environment_values(monkeypatch: object) -> None:
    monkeypatch.setenv("APP_NAME", "Test App")
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("DATABASE_ENGINE", "sqlite")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///tmp/test.db")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("OPENAI_API_KEY", "abc123")
    monkeypatch.setenv("OCR_ENGINE", "easyocr")
    monkeypatch.setenv("STORAGE_DRIVER", "local")
    monkeypatch.setenv("LOCAL_STORAGE_PATH", "test-storage")
    monkeypatch.setenv("TIMEZONE", "UTC")
    monkeypatch.setenv("DAILY_WISDOM_HOUR", "7")
    monkeypatch.setenv("SEARCH_ENGINE", "postgres")
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("CORS_ALLOW_ALL", "false")
    monkeypatch.setenv(
        "ALLOWED_ORIGINS", "https://app.example.com,https://admin.example.com"
    )
    monkeypatch.setenv("API_KEY", "test-api-key")

    settings = Settings(_env_file=None)

    assert settings.app_name == "Test App"
    assert settings.app_env == "testing"
    assert settings.debug is True
    assert settings.telegram_bot_token == "test-token"
    assert settings.database_engine == "sqlite"
    assert settings.database_url == "sqlite:///tmp/test.db"
    assert settings.log_level == "DEBUG"
    assert settings.openai_api_key == "abc123"
    assert settings.ocr_engine == "easyocr"
    assert settings.storage_driver == "local"
    assert settings.local_storage_path == "test-storage"
    assert settings.timezone == "UTC"
    assert settings.daily_wisdom_hour == 7
    assert settings.search_engine == "postgres"
    assert settings.ai_provider == "openai"
    assert settings.cors_allow_all is False
    assert settings.allowed_origins == [
        "https://app.example.com",
        "https://admin.example.com",
    ]
    assert settings.api_key == "test-api-key"
