from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_system_metadata import (
    AppRegistryEndpoint,
    AppRegistryHealthCheck,
    AppRegistryHealthCheckRun,
)


class AppRegistryRuntimeGovernanceSaveError(ValueError):
    pass


class AppRegistryRuntimeGovernanceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_health_check(self, health_check_id: int) -> AppRegistryHealthCheck | None:
        return (
            self.db.query(AppRegistryHealthCheck)
            .filter(AppRegistryHealthCheck.id == health_check_id)
            .one_or_none()
        )

    def get_endpoint(self, endpoint_id: int) -> AppRegistryEndpoint | None:
        return (
            self.db.query(AppRegistryEndpoint)
            .filter(AppRegistryEndpoint.id == endpoint_id)
            .one_or_none()
        )

    def create_health_check_run(
        self,
        row: AppRegistryHealthCheckRun,
    ) -> AppRegistryHealthCheckRun:
        self.db.add(row)

        try:
            self.db.commit()
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise AppRegistryRuntimeGovernanceSaveError("健康检查执行结果保存失败") from exc

        self.db.refresh(row)
        return row


__all__ = [
    "AppRegistryRuntimeGovernanceRepository",
    "AppRegistryRuntimeGovernanceSaveError",
]
