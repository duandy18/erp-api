from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Protocol

from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryDependency,
    AppRegistryEndpoint,
    AppRegistryHealthCheck,
    AppRegistryHealthCheckRun,
    AppRegistryOpenApiSource,
)
from app.system_monitoring.contracts.system_monitoring_contracts import (
    SystemMonitoringAppStatusOut,
    SystemMonitoringOverviewOut,
    SystemMonitoringStatus,
    SystemMonitoringSummaryOut,
)
from app.system_monitoring.repositories.system_monitoring_repository import (
    SystemMonitoringRepository,
)


class _AppCodeRow(Protocol):
    app_code: object


_STATUS_PRIORITY: dict[SystemMonitoringStatus, int] = {
    "ok": 0,
    "not_configured": 1,
    "unchecked": 2,
    "warning": 3,
    "timeout": 4,
    "error": 5,
}


def _group_by_app[T: _AppCodeRow](rows: list[T]) -> dict[str, list[T]]:
    grouped: dict[str, list[T]] = defaultdict(list)
    for row in rows:
        grouped[str(row.app_code)].append(row)
    return grouped


def _worst_status(statuses: list[SystemMonitoringStatus]) -> SystemMonitoringStatus:
    if not statuses:
        return "not_configured"

    return max(statuses, key=lambda status: _STATUS_PRIORITY[status])


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


def _latest_run_time(
    checks: list[AppRegistryHealthCheck],
    latest_run_by_check_id: dict[int, AppRegistryHealthCheckRun],
) -> datetime | None:
    candidates: list[datetime] = []

    for check in checks:
        run = latest_run_by_check_id.get(int(check.id))
        if run is None:
            continue

        candidates.append(run.finished_at or run.started_at)

    return max(candidates) if candidates else None


def _health_status(
    *,
    endpoint_type: str,
    checks: list[AppRegistryHealthCheck],
    endpoint_by_id: dict[int, AppRegistryEndpoint],
    latest_run_by_check_id: dict[int, AppRegistryHealthCheckRun],
) -> SystemMonitoringStatus:
    relevant_checks = [
        check
        for check in checks
        if check.is_active
        and (endpoint := endpoint_by_id.get(int(check.endpoint_id))) is not None
        and endpoint.endpoint_type == endpoint_type
    ]

    if not relevant_checks:
        return "not_configured"

    return _worst_status(
        [_run_status(latest_run_by_check_id.get(int(check.id))) for check in relevant_checks]
    )


def _gateway_status(rows: list[object]) -> SystemMonitoringStatus:
    active_rows = [row for row in rows if bool(getattr(row, "is_active", False))]
    if not active_rows:
        return "not_configured"

    return "ok"


def _openapi_status(rows: list[AppRegistryOpenApiSource]) -> SystemMonitoringStatus:
    active_rows = [row for row in rows if bool(row.is_active)]
    if not active_rows:
        return "not_configured"

    statuses: list[SystemMonitoringStatus] = []
    for row in active_rows:
        last_status = str(row.last_status)
        if last_status == "success":
            statuses.append("ok")
        elif last_status == "failure":
            statuses.append("error")
        else:
            statuses.append("unchecked")

    return _worst_status(statuses)


def _service_auth_status(
    *,
    service_clients: list[object],
    service_permissions: list[object],
) -> SystemMonitoringStatus:
    if not service_clients and not service_permissions:
        return "not_configured"

    if any(bool(getattr(row, "is_active", False)) for row in service_clients):
        return "ok"

    if any(bool(getattr(row, "is_active", False)) for row in service_permissions):
        return "ok"

    return "warning"


def _dependency_status(rows: list[AppRegistryDependency]) -> SystemMonitoringStatus:
    active_rows = [row for row in rows if bool(row.is_active)]
    if not active_rows:
        return "not_configured"

    statuses = {str(row.status) for row in active_rows}
    if "deprecated" in statuses:
        return "warning"
    if statuses - {"ready"}:
        return "unchecked"

    return "ok"


def _overall_status(statuses: list[SystemMonitoringStatus]) -> SystemMonitoringStatus:
    if any(status in {"error", "timeout"} for status in statuses):
        return "error"
    if "warning" in statuses:
        return "warning"
    if any(status in {"unchecked", "not_configured"} for status in statuses):
        return "unchecked"

    return "ok"


def _issue_summary(
    status_by_label: list[tuple[str, SystemMonitoringStatus]],
) -> str | None:
    messages: dict[SystemMonitoringStatus, str] = {
        "not_configured": "未配置",
        "unchecked": "未检查",
        "warning": "待完善",
        "timeout": "超时",
        "error": "异常",
        "ok": "正常",
    }

    for label, status in status_by_label:
        if status != "ok":
            return f"{label}{messages[status]}"

    return None


class SystemMonitoringService:
    def __init__(self, db: Session) -> None:
        self.repo = SystemMonitoringRepository(db)

    def get_overview(self) -> SystemMonitoringOverviewOut:
        apps = self.repo.list_apps()
        endpoints = self.repo.list_endpoints()
        health_checks = self.repo.list_health_checks()
        health_check_ids = {int(row.id) for row in health_checks}
        latest_runs = self.repo.list_latest_health_check_runs(health_check_ids)

        endpoint_by_id = {int(row.id): row for row in endpoints}
        latest_run_by_check_id: dict[int, AppRegistryHealthCheckRun] = {}
        for row in latest_runs:
            health_check_id = int(row.health_check_id)
            if health_check_id not in latest_run_by_check_id:
                latest_run_by_check_id[health_check_id] = row

        gateway_by_app = _group_by_app(self.repo.list_gateway_bindings())
        health_checks_by_app = _group_by_app(health_checks)
        openapi_by_app = _group_by_app(self.repo.list_openapi_sources())
        service_clients_by_app = _group_by_app(self.repo.list_service_clients())
        service_permissions_by_source = _group_by_app(self.repo.list_service_permissions())

        dependency_by_app: dict[str, list[AppRegistryDependency]] = defaultdict(list)
        for row in self.repo.list_dependencies():
            dependency_by_app[str(row.source_app_code)].append(row)
            dependency_by_app[str(row.target_app_code)].append(row)

        app_statuses = [
            self._build_app_status(
                app=app,
                endpoint_by_id=endpoint_by_id,
                latest_run_by_check_id=latest_run_by_check_id,
                gateway_rows=gateway_by_app[str(app.code)],
                health_checks=health_checks_by_app[str(app.code)],
                openapi_rows=openapi_by_app[str(app.code)],
                service_client_rows=service_clients_by_app[str(app.code)],
                service_permission_rows=service_permissions_by_source[str(app.code)],
                dependency_rows=dependency_by_app[str(app.code)],
            )
            for app in apps
        ]

        return SystemMonitoringOverviewOut(
            summary=self._build_summary(app_statuses),
            apps=app_statuses,
        )

    def _build_app_status(
        self,
        *,
        app: AppRegistryApp,
        endpoint_by_id: dict[int, AppRegistryEndpoint],
        latest_run_by_check_id: dict[int, AppRegistryHealthCheckRun],
        gateway_rows: list[object],
        health_checks: list[AppRegistryHealthCheck],
        openapi_rows: list[AppRegistryOpenApiSource],
        service_client_rows: list[object],
        service_permission_rows: list[object],
        dependency_rows: list[AppRegistryDependency],
    ) -> SystemMonitoringAppStatusOut:
        gateway_status = _gateway_status(gateway_rows)
        api_health_status = _health_status(
            endpoint_type="health",
            checks=health_checks,
            endpoint_by_id=endpoint_by_id,
            latest_run_by_check_id=latest_run_by_check_id,
        )
        db_health_status = _health_status(
            endpoint_type="db_health",
            checks=health_checks,
            endpoint_by_id=endpoint_by_id,
            latest_run_by_check_id=latest_run_by_check_id,
        )
        openapi_status = _openapi_status(openapi_rows)
        service_auth_status = _service_auth_status(
            service_clients=service_client_rows,
            service_permissions=service_permission_rows,
        )
        dependency_status = _dependency_status(dependency_rows)

        status_by_label = [
            ("Gateway", gateway_status),
            ("API Health", api_health_status),
            ("DB Health", db_health_status),
            ("OpenAPI", openapi_status),
            ("Service Auth", service_auth_status),
            ("系统依赖", dependency_status),
        ]
        overall_status = _overall_status([status for _, status in status_by_label])

        return SystemMonitoringAppStatusOut(
            app_code=str(app.code),
            app_name=str(app.name),
            app_status=str(app.status),
            is_active=bool(app.is_active),
            web_path=str(app.web_path),
            api_path=str(app.api_path),
            gateway_status=gateway_status,
            api_health_status=api_health_status,
            db_health_status=db_health_status,
            openapi_status=openapi_status,
            service_auth_status=service_auth_status,
            dependency_status=dependency_status,
            overall_status=overall_status,
            latest_checked_at=_latest_run_time(health_checks, latest_run_by_check_id),
            issue_summary=_issue_summary(status_by_label),
        )

    @staticmethod
    def _build_summary(
        app_statuses: list[SystemMonitoringAppStatusOut],
    ) -> SystemMonitoringSummaryOut:
        normal_count = sum(1 for row in app_statuses if row.overall_status == "ok")
        warning_count = sum(1 for row in app_statuses if row.overall_status == "warning")
        error_count = sum(1 for row in app_statuses if row.overall_status == "error")
        unchecked_count = sum(1 for row in app_statuses if row.overall_status == "unchecked")

        return SystemMonitoringSummaryOut(
            app_count=len(app_statuses),
            normal_count=normal_count,
            warning_count=warning_count,
            error_count=error_count,
            unchecked_count=unchecked_count,
        )


__all__ = ["SystemMonitoringService"]
