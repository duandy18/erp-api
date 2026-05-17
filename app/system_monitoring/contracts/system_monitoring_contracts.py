from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SystemMonitoringStatus = Literal[
    "ok",
    "warning",
    "error",
    "timeout",
    "unchecked",
    "not_configured",
]


class _SystemMonitoringBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SystemMonitoringSummaryOut(_SystemMonitoringBase):
    app_count: int
    normal_count: int
    warning_count: int
    error_count: int
    unchecked_count: int


class SystemMonitoringAppStatusOut(_SystemMonitoringBase):
    app_code: str
    app_name: str
    app_status: str
    is_active: bool
    web_path: str
    api_path: str
    gateway_status: SystemMonitoringStatus
    api_health_status: SystemMonitoringStatus
    db_health_status: SystemMonitoringStatus
    openapi_status: SystemMonitoringStatus
    service_auth_status: SystemMonitoringStatus
    dependency_status: SystemMonitoringStatus
    overall_status: SystemMonitoringStatus
    latest_checked_at: datetime | None
    issue_summary: str | None


class SystemMonitoringOverviewOut(_SystemMonitoringBase):
    summary: SystemMonitoringSummaryOut
    apps: list[SystemMonitoringAppStatusOut] = Field(default_factory=list)


__all__ = [
    "SystemMonitoringAppStatusOut",
    "SystemMonitoringOverviewOut",
    "SystemMonitoringStatus",
    "SystemMonitoringSummaryOut",
]
