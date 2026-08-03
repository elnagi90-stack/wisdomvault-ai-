from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class DatabaseEngine(StrEnum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


class StorageDriver(StrEnum):
    LOCAL = "local"
    S3 = "s3"


class OcrEngine(StrEnum):
    EASYOCR = "easyocr"
    TESSERACT = "tesseract"
    PADDLEOCR = "paddleocr"


class SearchEngine(StrEnum):
    POSTGRES = "postgres"
    PGVECTOR = "pgvector"
    CHROMA = "chroma"
    FAISS = "faiss"


class AiProvider(StrEnum):
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    OLLAMA = "ollama"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = Field(default="WisdomVault AI")
    app_env: AppEnv = Field(default=AppEnv.DEVELOPMENT)
    debug: bool = Field(default=True)

    telegram_bot_token: str = Field(default="")

    database_engine: DatabaseEngine = Field(default=DatabaseEngine.SQLITE)
    database_url: str = Field(default="sqlite:///storage/database.db")

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")

    openai_api_key: str = Field(default="")

    ocr_engine: OcrEngine = Field(default=OcrEngine.EASYOCR)

    storage_driver: StorageDriver = Field(default=StorageDriver.LOCAL)
    local_storage_path: str = Field(default="storage")
    s3_bucket: str = Field(default="")
    s3_region: str = Field(default="")
    s3_access_key: str = Field(default="")
    s3_secret_key: str = Field(default="")

    timezone: str = Field(default="Africa/Cairo")
    daily_wisdom_hour: int = Field(default=9, ge=0, le=23)

    search_engine: SearchEngine = Field(default=SearchEngine.POSTGRES)

    ai_provider: AiProvider = Field(default=AiProvider.OPENAI)

    @field_validator("app_env", mode="before")
    @classmethod
    def validate_app_env(cls, value: object) -> object:
        if isinstance(value, AppEnv):
            return value
        if isinstance(value, str):
            return value.lower()
        return value

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value:
            raise ValueError("DATABASE_URL cannot be empty")
        return value

    @field_validator("telegram_bot_token")
    @classmethod
    def validate_telegram_bot_token(cls, value: str) -> str:
        if value == "YOUR_BOT_TOKEN_HERE":
            return ""
        return value

    @property
    def is_development(self) -> bool:
        return self.app_env == AppEnv.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        return self.app_env == AppEnv.TESTING

    @property
    def is_production(self) -> bool:
        return self.app_env == AppEnv.PRODUCTION

    @property
    def storage_path(self) -> Path:
        return Path(self.local_storage_path)


try:
    settings = Settings()
except ValidationError as exc:  # pragma: no cover - defensive import path
    settings = Settings(_env_file=None)
