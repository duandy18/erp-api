from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.system_monitoring.contracts.system_monitoring_contracts import SystemMonitoringStatus

SystemMonitoringCheckTarget = Literal[
    "gateway",
    "dependency",
    "service_client",
    "service_permission",
    "openapi",
]

JsonScalar = str | int | float | bool | None


class _SystemMonitoringCheckBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SystemMonitoringCheckResultOut(_SystemMonitoringCheckBase):
    target_type: SystemMonitoringCheckTarget
    target_id: int
    status: SystemMonitoringStatus
    checked_at: datetime
    message: str
    details: dict[str, JsonScalar] = Field(default_factory=dict)


__all__ = [
    "JsonScalar",
    "SystemMonitoringCheckResultOut",
    "SystemMonitoringCheckTarget",
]
