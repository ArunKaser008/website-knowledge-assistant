#This file centralizes application settings.

#BaseSettings: Reads configuration from environment variables and .env.
#DATABASE_URL: Holds the PostgreSQL connection string.
#PROJECT_ROOT: Locates .env relative to the Python file, so the configuration doesn't depend on which directory you launch the application from.
#settings: A shared configuration object that other modules can import.

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Resolve the .env file from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):

    APP_NAME: str = "Website Knowledge Assistant"
    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()