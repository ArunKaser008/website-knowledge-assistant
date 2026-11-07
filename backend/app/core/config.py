
"""Centralized application settings."""

from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


# Resolve .env from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):

    APP_NAME: str = "Website Knowledge Assistant"
    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str

    # Gemini API configuration.
    GEMINI_API_KEY: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
