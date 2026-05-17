from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.system_monitoring.contracts.system_monitoring_contracts import SystemMonitoringStatus


class _SystemMonitoringRemainingBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SystemMonitoringGatewayBindingOut(_SystemMonitoringRemainingBase):
    binding_id: int
    app_code: str
    app_name: str
    env_code: str
    web_path: str
    api_path: str
    web_upstream_url: str | None
    api_upstream_url: str | None
    rewrite_mode: str
    is_published: bool
    published_at: datetime | None
    binding_active: bool
    status: SystemMonitoringStatus
    issue_summary: str | None


class SystemMonitoringGatewayBindingListOut(_SystemMonitoringRemainingBase):
    gateway_bindings: list[SystemMonitoringGatewayBindingOut] = Field(default_factory=list)


class SystemMonitoringDependencyOut(_SystemMonitoringRemainingBase):
    dependency_id: int
    source_app_code: str
    source_app_name: str
    target_app_code: str
    target_app_name: str
    dependency_type: str
    description: str
    is_required: bool
    dependency_status: str
    dependency_active: bool
    status: SystemMonitoringStatus
    issue_summary: str | None


class SystemMonitoringDependencyListOut(_SystemMonitoringRemainingBase):
    dependencies: list[SystemMonitoringDependencyOut] = Field(default_factory=list)


class SystemMonitoringServiceClientOut(_SystemMonitoringRemainingBase):
    client_id: int
    app_code: str
    app_name: str
    client_code: str
    client_name: str
    auth_type: str
    secret_ref: str | None
    client_active: bool
    status: SystemMonitoringStatus
    issue_summary: str | None


class SystemMonitoringServicePermissionOut(_SystemMonitoringRemainingBase):
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
    status: SystemMonitoringStatus
    issue_summary: str | None


class SystemMonitoringServiceAuthOut(_SystemMonitoringRemainingBase):
    clients: list[SystemMonitoringServiceClientOut] = Field(default_factory=list)
    permissions: list[SystemMonitoringServicePermissionOut] = Field(default_factory=list)


class SystemMonitoringOpenApiSourceOut(_SystemMonitoringRemainingBase):
    source_id: int
    app_code: str
    app_name: str
    env_code: str
    endpoint_id: int
    endpoint_url: str | None
    openapi_url: str
    last_fetched_at: datetime | None
    last_checksum: str | None
    last_status: str
    source_active: bool
    status: SystemMonitoringStatus
    issue_summary: str | None


class SystemMonitoringOpenApiSourceListOut(_SystemMonitoringRemainingBase):
    openapi_sources: list[SystemMonitoringOpenApiSourceOut] = Field(default_factory=list)


class SystemMonitoringHealthCheckOut(_SystemMonitoringRemainingBase):
    health_check_id: int
    app_code: str
    app_name: str
    env_code: str
    endpoint_id: int
    endpoint_type: str | None
    endpoint_name: str | None
    endpoint_url: str | None
    check_type: str
    expected_status: int
    timeout_ms: int
    interval_seconds: int
    severity: str
    check_active: bool
    endpoint_active: bool
    status: SystemMonitoringStatus
    http_status: int | None
    latency_ms: int | None
    latest_checked_at: datetime | None
    issue_summary: str | None


class SystemMonitoringHealthCheckListOut(_SystemMonitoringRemainingBase):
    health_checks: list[SystemMonitoringHealthCheckOut] = Field(default_factory=list)


__all__ = [
    "SystemMonitoringDependencyListOut",
    "SystemMonitoringDependencyOut",
    "SystemMonitoringGatewayBindingListOut",
    "SystemMonitoringGatewayBindingOut",
    "SystemMonitoringHealthCheckListOut",
    "SystemMonitoringHealthCheckOut",
    "SystemMonitoringOpenApiSourceListOut",
    "SystemMonitoringOpenApiSourceOut",
    "SystemMonitoringServiceAuthOut",
    "SystemMonitoringServiceClientOut",
    "SystemMonitoringServicePermissionOut",
]
