from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.system_monitoring.contracts.system_monitoring_contracts import SystemMonitoringStatus


class _SystemMonitoringDatabaseBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SystemMonitoringDatabaseStatusOut(_SystemMonitoringDatabaseBase):
    app_code: str
    app_name: str
    env_code: str
    database_id: int
    db_engine: str
    db_host_label: str
    db_port: int
    db_name: str
    schema_name: str
    migration_tool: str | None
    migration_command: str | None
    access_policy: str
    database_active: bool
    health_endpoint_id: int | None
    health_url: str | None
    health_endpoint_active: bool
    health_check_id: int | None
    status: SystemMonitoringStatus
    http_status: int | None
    latency_ms: int | None
    latest_checked_at: datetime | None
    issue_summary: str | None


class SystemMonitoringDatabaseStatusListOut(_SystemMonitoringDatabaseBase):
    databases: list[SystemMonitoringDatabaseStatusOut] = Field(default_factory=list)


__all__ = [
    "SystemMonitoringDatabaseStatusListOut",
    "SystemMonitoringDatabaseStatusOut",
]
