from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.system_monitoring.contracts.system_monitoring_contracts import SystemMonitoringStatus


class _SystemMonitoringEndpointBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SystemMonitoringEndpointStatusOut(_SystemMonitoringEndpointBase):
    app_code: str
    app_name: str
    env_code: str | None
    api_endpoint_id: int | None
    health_endpoint_id: int | None
    api_url: str | None
    health_url: str | None
    api_endpoint_active: bool
    health_endpoint_active: bool
    health_check_id: int | None
    status: SystemMonitoringStatus
    http_status: int | None
    latency_ms: int | None
    latest_checked_at: datetime | None
    issue_summary: str | None


class SystemMonitoringEndpointStatusListOut(_SystemMonitoringEndpointBase):
    endpoints: list[SystemMonitoringEndpointStatusOut] = Field(default_factory=list)


__all__ = [
    "SystemMonitoringEndpointStatusListOut",
    "SystemMonitoringEndpointStatusOut",
]
