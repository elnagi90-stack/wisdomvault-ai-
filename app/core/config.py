from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, EnvSettingsSource, PydanticBaseSettingsSource, SettingsConfigDict


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


class CustomEnvSettingsSource(EnvSettingsSource):
    def decode_complex_value(self, field_name: str, field: object, value: object) -> object:
        if field_name == "allowed_origins" and isinstance(value, str):
            if not value:
                return []
            return [item.strip() for item in value.split(",") if item.strip()]
        return super().decode_complex_value(field_name, field, value)


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

    # CORS configuration
    cors_allow_all: bool = Field(default=True)
    allowed_origins: list[str] = Field(default_factory=list)

    # Optional API key for protecting write endpoints (leave empty to disable)
    api_key: str = Field(default="")

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

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> list[str]:
        if isinstance(value, str):
            if not value:
                return []
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, (list, tuple)):
            return [str(item).strip() for item in value if str(item).strip()]
        return []

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            CustomEnvSettingsSource(settings_cls=settings_cls),
            dotenv_settings,
            file_secret_settings,
        )

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
