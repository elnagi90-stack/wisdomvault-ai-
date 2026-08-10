from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


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
            return [x.strip() for x in value.split(",") if x.strip()]
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
    tavily_api_key: str = Field(default="")

    # Minimum RAW semantic similarity (cosine similarity from the
    # embedding model, before any source-quality bonus) a web-search
    # candidate must reach to be considered a genuine match at all.
    # Kept intentionally moderate: real "similar in meaning" quotes
    # (not just near-duplicates) commonly land around 0.4-0.6 with
    # BAAI/bge-m3, while unrelated text usually falls well below 0.3.
    min_semantic_similarity: float = Field(default=0.35)

    secret_key: str = Field(default="change-this-secret-key-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60)

    # Notion OAuth integration
    notion_client_id: str = Field(default="")
    notion_client_secret: str = Field(default="")
    notion_redirect_uri: str = Field(
        default="http://127.0.0.1:8000/api/v1/notion/callback"
    )

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

    cors_allow_all: bool = Field(default=True)
    allowed_origins: list[str] = Field(default_factory=list)

    api_key: str = Field(default="")

    @field_validator("app_env", mode="before")
    @classmethod
    def validate_app_env(cls, value):
        if isinstance(value, AppEnv):
            return value
        if isinstance(value, str):
            return value.lower()
        return value

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value):
        if not value:
            raise ValueError("DATABASE_URL cannot be empty")
        return value

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            CustomEnvSettingsSource(settings_cls=settings_cls),
            dotenv_settings,
            file_secret_settings,
        )

    @property
    def storage_path(self):
        return Path(self.local_storage_path)


try:
    settings = Settings()
except ValidationError:
    settings = Settings(_env_file=None)
