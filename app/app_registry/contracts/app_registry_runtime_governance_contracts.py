from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class _RuntimeGovernanceBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AppRegistryHealthCheckRunOut(_RuntimeGovernanceBase):
    id: int
    health_check_id: int
    started_at: datetime
    finished_at: datetime | None
    status: str
    http_status: int | None
    latency_ms: int | None
    message: str | None
    raw_excerpt: str | None


__all__ = ["AppRegistryHealthCheckRunOut"]
