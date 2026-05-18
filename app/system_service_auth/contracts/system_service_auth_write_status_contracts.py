from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class _SystemServiceAuthWriteStatusBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SystemServiceAuthWriteRunOut(_SystemServiceAuthWriteStatusBase):
    run_id: int
    permission_id: int
    source_app_code: str
    target_app_code: str
    client_code: str | None
    permission_code: str
    operation: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    target_base_url: str | None
    http_status: int | None
    error_message: str | None
    raw_excerpt: str | None


class SystemServiceAuthWriteStatusItemOut(_SystemServiceAuthWriteStatusBase):
    permission_id: int
    client_id: int
    client_code: str | None
    source_app_code: str
    source_app_name: str
    target_app_code: str
    target_app_name: str
    permission_code: str
    description: str
    permission_active: bool
    latest_run: SystemServiceAuthWriteRunOut | None


class SystemServiceAuthWriteStatusListOut(_SystemServiceAuthWriteStatusBase):
    items: list[SystemServiceAuthWriteStatusItemOut] = Field(default_factory=list)
    recent_runs: list[SystemServiceAuthWriteRunOut] = Field(default_factory=list)


__all__ = [
    "SystemServiceAuthWriteRunOut",
    "SystemServiceAuthWriteStatusItemOut",
    "SystemServiceAuthWriteStatusListOut",
]
