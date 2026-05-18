from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class _SystemServiceAuthPermissionBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SystemServiceAuthClientOut(_SystemServiceAuthPermissionBase):
    client_id: int
    app_code: str
    app_name: str
    client_code: str
    client_name: str
    auth_type: str
    secret_ref: str | None
    is_active: bool


class SystemServiceAuthCapabilityOptionOut(_SystemServiceAuthPermissionBase):
    target_app_code: str
    target_app_name: str
    capability_code: str
    capability_name: str
    permission_code: str
    description: str | None
    is_active: bool
    last_synced_at: datetime | None


class SystemServiceAuthPermissionOut(_SystemServiceAuthPermissionBase):
    permission_id: int
    client_id: int
    client_code: str | None
    source_app_code: str
    source_app_name: str
    target_app_code: str
    target_app_name: str
    permission_code: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    capability_code: str | None
    capability_name: str | None
    capability_active: bool | None


class SystemServiceAuthPermissionListOut(_SystemServiceAuthPermissionBase):
    clients: list[SystemServiceAuthClientOut] = Field(default_factory=list)
    capability_options: list[SystemServiceAuthCapabilityOptionOut] = Field(default_factory=list)
    permissions: list[SystemServiceAuthPermissionOut] = Field(default_factory=list)


class SystemServiceAuthPermissionCreateIn(_SystemServiceAuthPermissionBase):
    client_id: int
    target_app_code: str
    permission_code: str
    description: str
    is_active: bool = False


class SystemServiceAuthPermissionUpdateIn(_SystemServiceAuthPermissionBase):
    description: str | None = None
    is_active: bool | None = None


__all__ = [
    "SystemServiceAuthCapabilityOptionOut",
    "SystemServiceAuthClientOut",
    "SystemServiceAuthPermissionCreateIn",
    "SystemServiceAuthPermissionListOut",
    "SystemServiceAuthPermissionOut",
    "SystemServiceAuthPermissionUpdateIn",
]
