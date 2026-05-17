from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryEndpoint,
    AppRegistryHealthCheck,
    AppRegistryHealthCheckRun,
)
from app.system_monitoring.contracts.system_monitoring_contracts import SystemMonitoringStatus
from app.system_monitoring.contracts.system_monitoring_endpoint_contracts import (
    SystemMonitoringEndpointStatusListOut,
    SystemMonitoringEndpointStatusOut,
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
    api_endpoint: AppRegistryEndpoint | None,
    health_endpoint: AppRegistryEndpoint | None,
    health_check: AppRegistryHealthCheck | None,
    run: AppRegistryHealthCheckRun | None,
    status: SystemMonitoringStatus,
) -> str | None:
    if api_endpoint is None:
        return "API 端点未配置"

    if health_endpoint is None:
        return "Health 端点未配置"

    if not api_endpoint.is_active:
        return "API 端点未启用"

    if not health_endpoint.is_active:
        return "Health 端点未启用"

    if health_check is None:
        return "API Health 检查未配置"

    if not health_check.is_active:
        return "API Health 检查未启用"

    if run is None:
        return "API Health 未检查"

    if status == "ok":
        return None

    if run.message:
        return str(run.message)

    return "API Health 状态异常"


class SystemMonitoringEndpointService:
    def __init__(self, db: Session) -> None:
        self.repo = SystemMonitoringRepository(db)

    def list_endpoint_statuses(self) -> SystemMonitoringEndpointStatusListOut:
        apps = self.repo.list_apps()
        endpoints = self.repo.list_endpoints()
        health_checks = self.repo.list_health_checks()
        health_check_ids = {int(row.id) for row in health_checks}
        latest_runs = self.repo.list_latest_health_check_runs(health_check_ids)

        endpoint_by_id = {int(row.id): row for row in endpoints}

        endpoints_by_app_type: dict[str, dict[str, list[AppRegistryEndpoint]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for row in endpoints:
            endpoints_by_app_type[str(row.app_code)][str(row.endpoint_type)].append(row)

        health_checks_by_app: dict[str, list[AppRegistryHealthCheck]] = defaultdict(list)
        for row in health_checks:
            health_checks_by_app[str(row.app_code)].append(row)

        latest_run_by_check_id: dict[int, AppRegistryHealthCheckRun] = {}
        for row in latest_runs:
            health_check_id = int(row.health_check_id)
            if health_check_id not in latest_run_by_check_id:
                latest_run_by_check_id[health_check_id] = row

        return SystemMonitoringEndpointStatusListOut(
            endpoints=[
                self._build_endpoint_status(
                    app=app,
                    endpoints_by_type=endpoints_by_app_type[str(app.code)],
                    health_checks=health_checks_by_app[str(app.code)],
                    endpoint_by_id=endpoint_by_id,
                    latest_run_by_check_id=latest_run_by_check_id,
                )
                for app in apps
            ]
        )

    def _build_endpoint_status(
        self,
        *,
        app: AppRegistryApp,
        endpoints_by_type: dict[str, list[AppRegistryEndpoint]],
        health_checks: list[AppRegistryHealthCheck],
        endpoint_by_id: dict[int, AppRegistryEndpoint],
        latest_run_by_check_id: dict[int, AppRegistryHealthCheckRun],
    ) -> SystemMonitoringEndpointStatusOut:
        api_endpoint = self._first_endpoint(endpoints_by_type, "api")
        health_endpoint = self._first_endpoint(endpoints_by_type, "health")
        health_check = self._find_health_check(
            health_endpoint=health_endpoint,
            health_checks=health_checks,
            endpoint_by_id=endpoint_by_id,
        )
        latest_run = (
            latest_run_by_check_id.get(int(health_check.id))
            if health_check is not None
            else None
        )

        status = self._derive_status(
            api_endpoint=api_endpoint,
            health_endpoint=health_endpoint,
            health_check=health_check,
            latest_run=latest_run,
        )

        return SystemMonitoringEndpointStatusOut(
            app_code=str(app.code),
            app_name=str(app.name),
            env_code=str(api_endpoint.env_code)
            if api_endpoint is not None
            else (
                str(health_endpoint.env_code)
                if health_endpoint is not None
                else None
            ),
            api_endpoint_id=int(api_endpoint.id) if api_endpoint is not None else None,
            health_endpoint_id=int(health_endpoint.id) if health_endpoint is not None else None,
            api_url=str(api_endpoint.url) if api_endpoint is not None else None,
            health_url=str(health_endpoint.url) if health_endpoint is not None else None,
            api_endpoint_active=bool(api_endpoint.is_active) if api_endpoint is not None else False,
            health_endpoint_active=bool(health_endpoint.is_active)
            if health_endpoint is not None
            else False,
            health_check_id=int(health_check.id) if health_check is not None else None,
            status=status,
            http_status=latest_run.http_status if latest_run is not None else None,
            latency_ms=latest_run.latency_ms if latest_run is not None else None,
            latest_checked_at=_latest_checked_at(latest_run),
            issue_summary=_issue_summary(
                api_endpoint=api_endpoint,
                health_endpoint=health_endpoint,
                health_check=health_check,
                run=latest_run,
                status=status,
            ),
        )

    @staticmethod
    def _first_endpoint(
        endpoints_by_type: dict[str, list[AppRegistryEndpoint]],
        endpoint_type: str,
    ) -> AppRegistryEndpoint | None:
        rows = [row for row in endpoints_by_type.get(endpoint_type, []) if row.is_active]
        if rows:
            return rows[0]

        inactive_rows = endpoints_by_type.get(endpoint_type, [])
        return inactive_rows[0] if inactive_rows else None

    @staticmethod
    def _find_health_check(
        *,
        health_endpoint: AppRegistryEndpoint | None,
        health_checks: list[AppRegistryHealthCheck],
        endpoint_by_id: dict[int, AppRegistryEndpoint],
    ) -> AppRegistryHealthCheck | None:
        if health_endpoint is None:
            return None

        for check in health_checks:
            endpoint = endpoint_by_id.get(int(check.endpoint_id))
            if endpoint is None:
                continue

            if int(endpoint.id) == int(health_endpoint.id):
                return check

        return None

    @staticmethod
    def _derive_status(
        *,
        api_endpoint: AppRegistryEndpoint | None,
        health_endpoint: AppRegistryEndpoint | None,
        health_check: AppRegistryHealthCheck | None,
        latest_run: AppRegistryHealthCheckRun | None,
    ) -> SystemMonitoringStatus:
        if api_endpoint is None or health_endpoint is None or health_check is None:
            return "not_configured"

        if (
            not api_endpoint.is_active
            or not health_endpoint.is_active
            or not health_check.is_active
        ):
            return "warning"

        return _run_status(latest_run)


__all__ = ["SystemMonitoringEndpointService"]
