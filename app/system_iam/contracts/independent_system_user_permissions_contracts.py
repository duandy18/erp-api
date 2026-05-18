from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SystemIamSyncRunOut(_Base):
    id: int
    app_code: str
    source_base_url: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    source_snapshot_at: datetime | None
    fetched_count: int
    inserted_count: int
    updated_count: int
    deleted_count: int
    error_message: str | None
    raw_excerpt: str | None


class SystemIamAppOut(_Base):
    app_code: str
    app_name: str
    app_type: str
    status: str
    is_active: bool


class SystemIamUserOut(_Base):
    app_code: str
    source_user_id: int
    username: str
    is_active: bool
    full_name: str | None
    phone: str | None
    email: str | None
    last_synced_at: datetime | None


class SystemIamPermissionOut(_Base):
    app_code: str
    source_permission_id: int
    permission_code: str
    last_synced_at: datetime | None


class SystemIamUserPermissionOut(_Base):
    app_code: str
    source_user_id: int
    source_permission_id: int
    permission_code: str
    granted_at: datetime | None
    last_synced_at: datetime | None


class SystemIamPageOut(_Base):
    app_code: str
    page_code: str
    page_name: str
    parent_page_code: str | None
    level: int
    domain_code: str | None
    show_in_topbar: bool
    show_in_sidebar: bool
    inherit_permissions: bool
    read_permission_code: str | None
    write_permission_code: str | None
    sort_order: int | None
    is_active: bool | None
    last_synced_at: datetime | None


class SystemIamPageRoutePrefixOut(_Base):
    app_code: str
    page_code: str
    route_prefix: str
    sort_order: int | None
    is_active: bool | None
    last_synced_at: datetime | None


class IndependentSystemUserPermissionsOut(_Base):
    apps: list[SystemIamAppOut] = Field(default_factory=list)
    users: list[SystemIamUserOut] = Field(default_factory=list)
    permissions: list[SystemIamPermissionOut] = Field(default_factory=list)
    user_permissions: list[SystemIamUserPermissionOut] = Field(default_factory=list)
    page_registry: list[SystemIamPageOut] = Field(default_factory=list)
    page_route_prefixes: list[SystemIamPageRoutePrefixOut] = Field(default_factory=list)
    latest_sync_runs: list[SystemIamSyncRunOut] = Field(default_factory=list)


__all__ = [
    "IndependentSystemUserPermissionsOut",
    "SystemIamAppOut",
    "SystemIamPageOut",
    "SystemIamPageRoutePrefixOut",
    "SystemIamPermissionOut",
    "SystemIamSyncRunOut",
    "SystemIamUserOut",
    "SystemIamUserPermissionOut",
]
