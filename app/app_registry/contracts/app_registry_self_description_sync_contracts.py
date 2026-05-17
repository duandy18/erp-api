from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AppRegistrySelfDescriptionSyncRunOut(BaseModel):
    id: int
    app_code: str
    sync_type: str
    source_base_url: str
    status: str
    started_at: datetime
    finished_at: datetime | None

    fetched_count: int
    inserted_count: int
    updated_count: int
    deleted_count: int

    error_message: str | None
    raw_excerpt: str | None

    model_config = ConfigDict(extra="forbid")


__all__ = ["AppRegistrySelfDescriptionSyncRunOut"]
