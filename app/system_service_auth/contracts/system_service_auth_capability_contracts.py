from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class _SystemServiceAuthCapabilityBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SystemServiceAuthCapabilityRouteOut(_SystemServiceAuthCapabilityBase):
    http_method: str
    path: str
    route_name: str
    auth_required: bool
    is_active: bool
    source_created_at: datetime | None
    last_synced_at: datetime | None


class SystemServiceAuthCapabilityOut(_SystemServiceAuthCapabilityBase):
    target_app_code: str
    target_app_name: str
    capability_code: str
    capability_name: str
    resource_code: str
    permission_code: str
    description: str | None
    is_active: bool
    source_updated_at: datetime | None
    last_synced_at: datetime | None
    route_count: int
    routes: list[SystemServiceAuthCapabilityRouteOut] = Field(default_factory=list)


class SystemServiceAuthCapabilityListOut(_SystemServiceAuthCapabilityBase):
    capabilities: list[SystemServiceAuthCapabilityOut] = Field(default_factory=list)


__all__ = [
    "SystemServiceAuthCapabilityListOut",
    "SystemServiceAuthCapabilityOut",
    "SystemServiceAuthCapabilityRouteOut",
]
