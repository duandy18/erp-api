from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import ping_database

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {
        "service": "erp-api",
        "status": "ok",
    }


@router.get("/health/db")
def health_db() -> dict[str, str]:
    try:
        ping_database()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc

    return {
        "database": "erp",
        "status": "ok",
    }
