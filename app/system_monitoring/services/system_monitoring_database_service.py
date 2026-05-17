from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryDatabase,
    AppRegistryEndpoint,
    AppRegistryHealthCheck,
    AppRegistryHealthCheckRun,
)
from app.system_monitoring.contracts.system_monitoring_contracts import SystemMonitoringStatus
from app.system_monitoring.contracts.system_monitoring_database_contracts import (
    SystemMonitoringDatabaseStatusListOut,
    SystemMonitoringDatabaseStatusOut,
)
from app.system_monitoring.repositories.system_monitoring_repository import (
    SystemMonitoringRepository,
)


def _latest_checked_at(run: AppRegistryHealthCheckRun | None) -> datetime | None:
    if run is None:
        return None

    return run.finished_at or run.started_at


def _run_status(run: AppRegistryHealthCheckRun | None) -> SystemMonitoringStatus:
    if run is None:
        return "unchecked"

    status = str(run.status)
    if status == "success":
        return "ok"
    if status == "timeout":
        return "timeout"
    if status in {"failure", "error"}:
        return "error"

    return "unchecked"


def _issue_summary(
    *,
    database: AppRegistryDatabase,
    health_endpoint: AppRegistryEndpoint | None,
    health_check: AppRegistryHealthCheck | None,
    run: AppRegistryHealthCheckRun | None,
    status: SystemMonitoringStatus,
) -> str | None:
    if not database.is_active:
        return "数据库登记未启用"

    if database.health_endpoint_id is None or health_endpoint is None:
        return "DB Health 端点未配置"

    if not health_endpoint.is_active:
        return "DB Health 端点未启用"

    if health_check is None:
        return "DB Health 检查未配置"

    if not health_check.is_active:
        return "DB Health 检查未启用"

    if run is None:
        return "DB Health 未检查"

    if status == "ok":
        return None

    if run.message:
        return str(run.message)

    return "DB Health 状态异常"


class SystemMonitoringDatabaseService:
    def __init__(self, db: Session) -> None:
        self.repo = SystemMonitoringRepository(db)

    def list_database_statuses(self) -> SystemMonitoringDatabaseStatusListOut:
        apps = self.repo.list_apps()
        app_by_code = {str(row.code): row for row in apps}

        endpoints = self.repo.list_endpoints()
        endpoint_by_id = {int(row.id): row for row in endpoints}

        health_checks = self.repo.list_health_checks()
        health_check_ids = {int(row.id) for row in health_checks}
        latest_runs = self.repo.list_latest_health_check_runs(health_check_ids)

        latest_run_by_check_id: dict[int, AppRegistryHealthCheckRun] = {}
        for row in latest_runs:
            health_check_id = int(row.health_check_id)
            if health_check_id not in latest_run_by_check_id:
                latest_run_by_check_id[health_check_id] = row

        health_check_by_endpoint_id: dict[int, AppRegistryHealthCheck] = {}
        for row in health_checks:
            endpoint_id = int(row.endpoint_id)
            if endpoint_id not in health_check_by_endpoint_id:
                health_check_by_endpoint_id[endpoint_id] = row

        return SystemMonitoringDatabaseStatusListOut(
            databases=[
                self._build_database_status(
                    database=database,
                    app=app_by_code.get(str(database.app_code)),
                    endpoint_by_id=endpoint_by_id,
                    health_check_by_endpoint_id=health_check_by_endpoint_id,
                    latest_run_by_check_id=latest_run_by_check_id,
                )
                for database in self.repo.list_databases()
            ]
        )

    def _build_database_status(
        self,
        *,
        database: AppRegistryDatabase,
        app: AppRegistryApp | None,
        endpoint_by_id: dict[int, AppRegistryEndpoint],
        health_check_by_endpoint_id: dict[int, AppRegistryHealthCheck],
        latest_run_by_check_id: dict[int, AppRegistryHealthCheckRun],
    ) -> SystemMonitoringDatabaseStatusOut:
        health_endpoint = (
            endpoint_by_id.get(int(database.health_endpoint_id))
            if database.health_endpoint_id is not None
            else None
        )
        health_check = (
            health_check_by_endpoint_id.get(int(health_endpoint.id))
            if health_endpoint is not None
            else None
        )
        latest_run = (
            latest_run_by_check_id.get(int(health_check.id))
            if health_check is not None
            else None
        )
        status = self._derive_status(
            database=database,
            health_endpoint=health_endpoint,
            health_check=health_check,
            latest_run=latest_run,
        )

        return SystemMonitoringDatabaseStatusOut(
            app_code=str(database.app_code),
            app_name=str(app.name) if app is not None else str(database.app_code),
            env_code=str(database.env_code),
            database_id=int(database.id),
            db_engine=str(database.db_engine),
            db_host_label=str(database.db_host_label),
            db_port=int(database.db_port),
            db_name=str(database.db_name),
            schema_name=str(database.schema_name),
            migration_tool=database.migration_tool,
            migration_command=database.migration_command,
            access_policy=str(database.access_policy),
            database_active=bool(database.is_active),
            health_endpoint_id=int(health_endpoint.id) if health_endpoint is not None else None,
            health_url=str(health_endpoint.url) if health_endpoint is not None else None,
            health_endpoint_active=bool(health_endpoint.is_active)
            if health_endpoint is not None
            else False,
            health_check_id=int(health_check.id) if health_check is not None else None,
            status=status,
            http_status=latest_run.http_status if latest_run is not None else None,
            latency_ms=latest_run.latency_ms if latest_run is not None else None,
            latest_checked_at=_latest_checked_at(latest_run),
            issue_summary=_issue_summary(
                database=database,
                health_endpoint=health_endpoint,
                health_check=health_check,
                run=latest_run,
                status=status,
            ),
        )

    @staticmethod
    def _derive_status(
        *,
        database: AppRegistryDatabase,
        health_endpoint: AppRegistryEndpoint | None,
        health_check: AppRegistryHealthCheck | None,
        latest_run: AppRegistryHealthCheckRun | None,
    ) -> SystemMonitoringStatus:
        if database.health_endpoint_id is None or health_endpoint is None or health_check is None:
            return "not_configured"

        if not database.is_active or not health_endpoint.is_active or not health_check.is_active:
            return "warning"

        return _run_status(latest_run)


__all__ = ["SystemMonitoringDatabaseService"]
