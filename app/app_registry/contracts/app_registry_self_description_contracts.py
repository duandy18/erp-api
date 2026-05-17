from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.app_registry.contracts.app_registry_self_description_sync_contracts import (
    AppRegistrySelfDescriptionSyncRunOut,
)


class _SelfDescriptionBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AppRegistrySelfDescriptionManifestOut(_SelfDescriptionBase):
    app_code: str
    app_name: str
    app_type: str
    status: str
    description: str

    default_web_path: str
    default_api_path: str
    local_web_url: str
    local_api_url: str

    health_url: str
    db_health_url: str | None
    openapi_url: str
    page_catalog_url: str
    service_capabilities_url: str
    service_dependencies_url: str

    version: str
    build_environment: str | None
    build_git_sha: str | None
    build_time: str | None

    last_synced_at: datetime | None


class AppRegistrySelfDescriptionPageOut(_SelfDescriptionBase):
    page_code: str
    page_name: str
    route_path: str | None
    parent_page_code: str | None
    level: int
    read_permission_code: str | None
    write_permission_code: str | None
    is_active: bool
    sort_order: int
    source_updated_at: datetime | None
    last_synced_at: datetime | None


class AppRegistrySelfDescriptionCapabilityRouteOut(_SelfDescriptionBase):
    http_method: str
    path: str
    route_name: str
    auth_required: bool
    is_active: bool
    source_created_at: datetime | None
    last_synced_at: datetime | None


class AppRegistrySelfDescriptionCapabilityOut(_SelfDescriptionBase):
    capability_code: str
    capability_name: str
    resource_code: str
    permission_code: str
    description: str | None
    is_active: bool
    source_updated_at: datetime | None
    last_synced_at: datetime | None
    routes: list[AppRegistrySelfDescriptionCapabilityRouteOut] = Field(default_factory=list)


class AppRegistrySelfDescriptionDependencyEndpointOut(_SelfDescriptionBase):
    http_method: str
    path: str
    purpose: str | None
    last_synced_at: datetime | None


class AppRegistrySelfDescriptionDependencyOut(_SelfDescriptionBase):
    dependency_code: str
    dependency_name: str
    target_app_code: str
    target_capability_code: str
    required_permission_code: str
    description: str | None
    is_required: bool
    is_active: bool
    required_config_keys: list[str] = Field(default_factory=list)
    source_modules: list[str] = Field(default_factory=list)
    last_synced_at: datetime | None
    endpoints: list[AppRegistrySelfDescriptionDependencyEndpointOut] = Field(
        default_factory=list
    )


class AppRegistrySelfDescriptionOut(_SelfDescriptionBase):
    app_code: str
    app_name: str

    manifest: AppRegistrySelfDescriptionManifestOut | None
    pages: list[AppRegistrySelfDescriptionPageOut] = Field(default_factory=list)
    capabilities: list[AppRegistrySelfDescriptionCapabilityOut] = Field(
        default_factory=list
    )
    dependencies: list[AppRegistrySelfDescriptionDependencyOut] = Field(
        default_factory=list
    )
    latest_sync_run: AppRegistrySelfDescriptionSyncRunOut | None


__all__ = [
    "AppRegistrySelfDescriptionCapabilityOut",
    "AppRegistrySelfDescriptionCapabilityRouteOut",
    "AppRegistrySelfDescriptionDependencyEndpointOut",
    "AppRegistrySelfDescriptionDependencyOut",
    "AppRegistrySelfDescriptionManifestOut",
    "AppRegistrySelfDescriptionOut",
    "AppRegistrySelfDescriptionPageOut",
]
