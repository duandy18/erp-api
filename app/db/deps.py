from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.database import get_engine


def get_db() -> Generator[Session]:
    with Session(get_engine()) as session:
        yield session


__all__ = ["get_db"]
