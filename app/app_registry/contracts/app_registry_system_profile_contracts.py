from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class _SystemProfileBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SystemProfileAppOut(_SystemProfileBase):
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


class SystemProfileComponentOut(_SystemProfileBase):
    id: int
    app_code: str
    component_code: str
    component_type: str
    name: str
    description: str
    is_required: bool
    is_active: bool
    sort_order: int


class SystemProfileEnvironmentOut(_SystemProfileBase):
    env_code: str
    name: str
    description: str
    sort_order: int
    is_active: bool


class SystemProfileAppEnvironmentOut(_SystemProfileBase):
    id: int
    app_code: str
    env_code: str
    display_name: str
    is_default: bool
    is_active: bool
    notes: str | None


class SystemProfileEndpointOut(_SystemProfileBase):
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


class SystemProfileDatabaseOut(_SystemProfileBase):
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


class SystemProfileRepositoryOut(_SystemProfileBase):
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


class SystemProfileGatewayBindingOut(_SystemProfileBase):
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


class SystemProfileDependencyOut(_SystemProfileBase):
    id: int
    source_app_code: str
    target_app_code: str
    dependency_type: str
    description: str
    is_required: bool
    status: str
    is_active: bool


class SystemProfileServiceClientOut(_SystemProfileBase):
    id: int
    app_code: str
    client_code: str
    client_name: str
    auth_type: str
    secret_ref: str | None
    is_active: bool


class SystemProfileServicePermissionOut(_SystemProfileBase):
    id: int
    client_id: int
    source_app_code: str
    target_app_code: str
    permission_code: str
    description: str
    is_active: bool


class AppRegistrySystemProfileOut(_SystemProfileBase):
    app: SystemProfileAppOut
    components: list[SystemProfileComponentOut] = Field(default_factory=list)
    environments: list[SystemProfileEnvironmentOut] = Field(default_factory=list)
    app_environments: list[SystemProfileAppEnvironmentOut] = Field(default_factory=list)
    endpoints: list[SystemProfileEndpointOut] = Field(default_factory=list)
    databases: list[SystemProfileDatabaseOut] = Field(default_factory=list)
    repositories: list[SystemProfileRepositoryOut] = Field(default_factory=list)
    gateway_bindings: list[SystemProfileGatewayBindingOut] = Field(default_factory=list)
    outgoing_dependencies: list[SystemProfileDependencyOut] = Field(default_factory=list)
    incoming_dependencies: list[SystemProfileDependencyOut] = Field(default_factory=list)
    service_clients: list[SystemProfileServiceClientOut] = Field(default_factory=list)
    service_permissions: list[SystemProfileServicePermissionOut] = Field(default_factory=list)


class AppRegistrySystemProfilesOut(_SystemProfileBase):
    profiles: list[AppRegistrySystemProfileOut] = Field(default_factory=list)


__all__ = [
    "AppRegistrySystemProfileOut",
    "AppRegistrySystemProfilesOut",
]
