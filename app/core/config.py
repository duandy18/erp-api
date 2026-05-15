from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = Field(default="local", validation_alias="ERP_ENV")
    api_port: int = Field(default=7990, validation_alias="ERP_API_PORT")
    database_url: str = Field(
        default="postgresql+psycopg://erp:erp@127.0.0.1:5433/erp",
        validation_alias="ERP_DATABASE_URL",
    )
    auth_secret: str = Field(
        default="erp-local-dev-secret-change-me",
        validation_alias="ERP_AUTH_SECRET",
    )
    access_token_expire_seconds: int = Field(
        default=7 * 24 * 60 * 60,
        validation_alias="ERP_ACCESS_TOKEN_EXPIRE_SECONDS",
    )

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
