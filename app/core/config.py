"""
AyuTrial-CTMS – Core Configuration
Pydantic Settings with environment variable support.
"""
from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database parameters (cleanly supports both standard 5432 and remapped 54321 host ports)
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "ayutrial"
    DB_PASSWORD: str = "ayutrial_secret"
    DB_NAME: str = "ayutrial_db"

    DATABASE_URL: str = "postgresql+asyncpg://ayutrial:ayutrial_secret@localhost:5432/ayutrial_db"
    SYNC_DATABASE_URL: str = "postgresql://ayutrial:ayutrial_secret@localhost:5432/ayutrial_db"

    @model_validator(mode="after")
    def assemble_db_urls(self) -> "Settings":
        if self.DB_PORT != 5432 or self.DB_HOST != "localhost":
            if "@localhost:5432/" in self.DATABASE_URL:
                self.DATABASE_URL = self.DATABASE_URL.replace(
                    "@localhost:5432/", f"@{self.DB_HOST}:{self.DB_PORT}/"
                )
            if "@localhost:5432/" in self.SYNC_DATABASE_URL:
                self.SYNC_DATABASE_URL = self.SYNC_DATABASE_URL.replace(
                    "@localhost:5432/", f"@{self.DB_HOST}:{self.DB_PORT}/"
                )
        return self

    # Security
    SECRET_KEY: str = "ayutrial-ctms-super-secret-key-change-in-prod-2026"

    # App
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    APP_TITLE: str = "AyuTrial-CTMS API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = (
        "Real-time GCP-compliant CTMS and NPvCC platform for AIIA. "
        "SIH Problem Statement ID: 26046."
    )

    # Audit
    GENESIS_HASH: str = "GENESIS_BLOCK_HASH_AIIA_CTMS_2026"


@lru_cache
def get_settings() -> Settings:
    return Settings()
