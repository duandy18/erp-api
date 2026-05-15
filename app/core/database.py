from __future__ import annotations

from sqlalchemy import Engine, create_engine, text

from app.core.config import get_settings

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine

    if _engine is None:
        settings = get_settings()
        _engine = create_engine(settings.database_url, pool_pre_ping=True)

    return _engine


def ping_database() -> None:
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))
