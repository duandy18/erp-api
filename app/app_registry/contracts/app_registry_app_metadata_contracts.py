from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class _AppMetadataBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AppMetadataAppOut(_AppMetadataBase):
    code: str
    name: str
    description: str
    web_path: str
    api_path: str
    local_web_url: str
    local_api_url: str
    status: str
    domain_code: str
    app_type: str
    owner_name: str | None
    owner_contact: str | None
    sort_order: int
    is_active: bool


class AppMetadataComponentOut(_AppMetadataBase):
    id: int
    app_code: str
    component_code: str
    component_type: str
    name: str
    description: str
    is_required: bool
    is_active: bool
    sort_order: int


class AppMetadataEnvironmentOut(_AppMetadataBase):
    env_code: str
    name: str
    description: str
    sort_order: int
    is_active: bool


class AppMetadataAppEnvironmentOut(_AppMetadataBase):
    id: int
    app_code: str
    env_code: str
    display_name: str
    is_default: bool
    is_active: bool
    notes: str | None


class AppMetadataEndpointOut(_AppMetadataBase):
    id: int
    app_code: str
    component_id: int | None
    env_code: str
    endpoint_type: str
    name: str
    method: str | None
    path: str | None
    url: str
    auth_required: bool
    timeout_ms: int
    is_active: bool
    sort_order: int


class AppMetadataDatabaseOut(_AppMetadataBase):
    id: int
    app_code: str
    env_code: str
    db_engine: str
    db_host_label: str
    db_port: int
    db_name: str
    schema_name: str
    migration_tool: str | None
    migration_command: str | None
    health_endpoint_id: int | None
    secret_ref: str | None
    access_policy: str
    is_active: bool
    notes: str | None


class AppMetadataRepositoryOut(_AppMetadataBase):
    id: int
    app_code: str
    component_id: int | None
    repo_type: str
    provider: str
    repo_owner: str
    repo_name: str
    default_branch: str
    local_path: str | None
    ci_workflow_name: str | None
    is_active: bool


class AppMetadataGatewayBindingOut(_AppMetadataBase):
    id: int
    app_code: str
    env_code: str
    web_path: str
    api_path: str
    web_upstream_url: str | None
    api_upstream_url: str | None
    rewrite_mode: str
    is_published: bool
    published_at: datetime | None
    is_active: bool


class AppMetadataDependencyOut(_AppMetadataBase):
    id: int
    source_app_code: str
    target_app_code: str
    dependency_type: str
    description: str
    is_required: bool
    status: str
    is_active: bool


class AppMetadataServiceClientOut(_AppMetadataBase):
    id: int
    app_code: str
    client_code: str
    client_name: str
    auth_type: str
    secret_ref: str | None
    is_active: bool


class AppMetadataServicePermissionOut(_AppMetadataBase):
    id: int
    client_id: int
    client_code: str | None
    client_name: str | None
    source_app_code: str
    target_app_code: str
    permission_code: str
    description: str
    is_active: bool


class AppMetadataHealthCheckRunOut(_AppMetadataBase):
    id: int
    health_check_id: int
    started_at: datetime
    finished_at: datetime | None
    status: str
    http_status: int | None
    latency_ms: int | None
    message: str | None
    raw_excerpt: str | None


class AppMetadataHealthCheckOut(_AppMetadataBase):
    id: int
    app_code: str
    env_code: str
    endpoint_id: int
    check_type: str
    expected_status: int
    expected_json_path: str | None
    expected_json_value: str | None
    timeout_ms: int
    interval_seconds: int
    severity: str
    is_active: bool
    latest_run: AppMetadataHealthCheckRunOut | None = None


class AppMetadataOpenApiSourceOut(_AppMetadataBase):
    id: int
    app_code: str
    env_code: str
    endpoint_id: int
    openapi_url: str
    last_fetched_at: datetime | None
    last_checksum: str | None
    last_status: str
    is_active: bool


class AppRegistryAppMetadataOut(_AppMetadataBase):
    app: AppMetadataAppOut
    components: list[AppMetadataComponentOut] = Field(default_factory=list)
    environments: list[AppMetadataEnvironmentOut] = Field(default_factory=list)
    app_environments: list[AppMetadataAppEnvironmentOut] = Field(default_factory=list)
    endpoints: list[AppMetadataEndpointOut] = Field(default_factory=list)
    databases: list[AppMetadataDatabaseOut] = Field(default_factory=list)
    repositories: list[AppMetadataRepositoryOut] = Field(default_factory=list)
    gateway_bindings: list[AppMetadataGatewayBindingOut] = Field(default_factory=list)
    outgoing_dependencies: list[AppMetadataDependencyOut] = Field(default_factory=list)
    incoming_dependencies: list[AppMetadataDependencyOut] = Field(default_factory=list)
    service_clients: list[AppMetadataServiceClientOut] = Field(default_factory=list)
    service_permissions: list[AppMetadataServicePermissionOut] = Field(default_factory=list)
    health_checks: list[AppMetadataHealthCheckOut] = Field(default_factory=list)
    openapi_sources: list[AppMetadataOpenApiSourceOut] = Field(default_factory=list)


class AppRegistryAppMetadataListOut(_AppMetadataBase):
    profiles: list[AppRegistryAppMetadataOut] = Field(default_factory=list)


__all__ = [
    "AppRegistryAppMetadataOut",
    "AppRegistryAppMetadataListOut",
]
