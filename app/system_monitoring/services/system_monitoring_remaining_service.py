from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryDependency,
    AppRegistryEndpoint,
    AppRegistryGatewayBinding,
    AppRegistryHealthCheck,
    AppRegistryHealthCheckRun,
    AppRegistryOpenApiSource,
    AppRegistryServiceClient,
    AppRegistryServicePermission,
)
from app.system_monitoring.contracts.system_monitoring_contracts import SystemMonitoringStatus
from app.system_monitoring.contracts.system_monitoring_remaining_contracts import (
    SystemMonitoringDependencyListOut,
    SystemMonitoringDependencyOut,
    SystemMonitoringGatewayBindingListOut,
    SystemMonitoringGatewayBindingOut,
    SystemMonitoringHealthCheckListOut,
    SystemMonitoringHealthCheckOut,
    SystemMonitoringOpenApiSourceListOut,
    SystemMonitoringOpenApiSourceOut,
    SystemMonitoringServiceAuthOut,
    SystemMonitoringServiceClientOut,
    SystemMonitoringServicePermissionOut,
)
from app.system_monitoring.repositories.system_monitoring_repository import (
    SystemMonitoringRepository,
)


def _app_name(app_by_code: dict[str, AppRegistryApp], app_code: object) -> str:
    code = str(app_code)
    app = app_by_code.get(code)
    return str(app.name) if app is not None else code


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


def _gateway_status(row: AppRegistryGatewayBinding) -> SystemMonitoringStatus:
    if not row.is_active:
        return "warning"
    if not row.web_path or not row.api_path:
        return "not_configured"
    if not row.is_published:
        return "warning"
    return "ok"


def _gateway_issue(row: AppRegistryGatewayBinding) -> str | None:
    if not row.is_active:
        return "Gateway 绑定未启用"
    if not row.web_path or not row.api_path:
        return "Gateway Web/API 路径未配置"
    if not row.is_published:
        return "Gateway 绑定未发布"
    return None


def _dependency_status(row: AppRegistryDependency) -> SystemMonitoringStatus:
    if not row.is_active:
        return "warning"

    status = str(row.status)
    if status == "ready":
        return "ok"
    if status == "planned":
        return "unchecked"
    if status == "deprecated":
        return "warning"

    return "warning"


def _dependency_issue(row: AppRegistryDependency) -> str | None:
    if not row.is_active:
        return "系统依赖未启用"

    status = str(row.status)
    if status == "ready":
        return None
    if status == "planned":
        return "系统依赖仍处于计划状态"
    if status == "deprecated":
        return "系统依赖已标记废弃"

    return "系统依赖状态待确认"


def _active_status(active: bool) -> SystemMonitoringStatus:
    return "ok" if active else "warning"


def _active_issue(active: bool, label: str) -> str | None:
    return None if active else f"{label}未启用"


def _openapi_status(row: AppRegistryOpenApiSource) -> SystemMonitoringStatus:
    if not row.is_active:
        return "warning"

    status = str(row.last_status)
    if status == "success":
        return "ok"
    if status == "failure":
        return "error"

    return "unchecked"


def _openapi_issue(row: AppRegistryOpenApiSource) -> str | None:
    if not row.is_active:
        return "OpenAPI 来源未启用"

    status = str(row.last_status)
    if status == "success":
        return None
    if status == "failure":
        return "OpenAPI 拉取失败"

    return "OpenAPI 尚未拉取"


def _health_status(
    *,
    endpoint: AppRegistryEndpoint | None,
    check: AppRegistryHealthCheck,
    run: AppRegistryHealthCheckRun | None,
) -> SystemMonitoringStatus:
    if endpoint is None:
        return "not_configured"

    if not endpoint.is_active or not check.is_active:
        return "warning"

    return _run_status(run)


def _health_issue(
    *,
    endpoint: AppRegistryEndpoint | None,
    check: AppRegistryHealthCheck,
    run: AppRegistryHealthCheckRun | None,
    status: SystemMonitoringStatus,
) -> str | None:
    if endpoint is None:
        return "健康检查端点不存在"
    if not endpoint.is_active:
        return "健康检查端点未启用"
    if not check.is_active:
        return "健康检查未启用"
    if run is None:
        return "健康检查尚未执行"
    if status == "ok":
        return None
    if run.message:
        return str(run.message)
    return "健康检查状态异常"


class SystemMonitoringRemainingService:
    def __init__(self, db: Session) -> None:
        self.repo = SystemMonitoringRepository(db)

    def list_gateway_bindings(self) -> SystemMonitoringGatewayBindingListOut:
        app_by_code = {str(row.code): row for row in self.repo.list_apps()}
        return SystemMonitoringGatewayBindingListOut(
            gateway_bindings=[
                self._gateway_out(row=row, app_by_code=app_by_code)
                for row in self.repo.list_gateway_bindings()
            ]
        )

    def list_dependencies(self) -> SystemMonitoringDependencyListOut:
        app_by_code = {str(row.code): row for row in self.repo.list_apps()}
        return SystemMonitoringDependencyListOut(
            dependencies=[
                self._dependency_out(row=row, app_by_code=app_by_code)
                for row in self.repo.list_dependencies()
            ]
        )

    def list_service_auth(self) -> SystemMonitoringServiceAuthOut:
        app_by_code = {str(row.code): row for row in self.repo.list_apps()}
        clients = self.repo.list_service_clients()
        client_by_id = {int(row.id): row for row in clients}

        return SystemMonitoringServiceAuthOut(
            clients=[
                self._service_client_out(row=row, app_by_code=app_by_code)
                for row in clients
            ],
            permissions=[
                self._service_permission_out(
                    row=row,
                    app_by_code=app_by_code,
                    client_by_id=client_by_id,
                )
                for row in self.repo.list_service_permissions()
            ],
        )

    def list_openapi_sources(self) -> SystemMonitoringOpenApiSourceListOut:
        app_by_code = {str(row.code): row for row in self.repo.list_apps()}
        endpoint_by_id = {int(row.id): row for row in self.repo.list_endpoints()}

        return SystemMonitoringOpenApiSourceListOut(
            openapi_sources=[
                self._openapi_out(
                    row=row,
                    app_by_code=app_by_code,
                    endpoint_by_id=endpoint_by_id,
                )
                for row in self.repo.list_openapi_sources()
            ]
        )

    def list_health_checks(self) -> SystemMonitoringHealthCheckListOut:
        app_by_code = {str(row.code): row for row in self.repo.list_apps()}
        endpoint_by_id = {int(row.id): row for row in self.repo.list_endpoints()}
        checks = self.repo.list_health_checks()
        latest_runs = self.repo.list_latest_health_check_runs({int(row.id) for row in checks})

        latest_run_by_check_id: dict[int, AppRegistryHealthCheckRun] = {}
        for row in latest_runs:
            check_id = int(row.health_check_id)
            if check_id not in latest_run_by_check_id:
                latest_run_by_check_id[check_id] = row

        return SystemMonitoringHealthCheckListOut(
            health_checks=[
                self._health_out(
                    row=row,
                    app_by_code=app_by_code,
                    endpoint_by_id=endpoint_by_id,
                    latest_run_by_check_id=latest_run_by_check_id,
                )
                for row in checks
            ]
        )

    @staticmethod
    def _gateway_out(
        *,
        row: AppRegistryGatewayBinding,
        app_by_code: dict[str, AppRegistryApp],
    ) -> SystemMonitoringGatewayBindingOut:
        status = _gateway_status(row)
        return SystemMonitoringGatewayBindingOut(
            binding_id=int(row.id),
            app_code=str(row.app_code),
            app_name=_app_name(app_by_code, row.app_code),
            env_code=str(row.env_code),
            web_path=str(row.web_path),
            api_path=str(row.api_path),
            web_upstream_url=row.web_upstream_url,
            api_upstream_url=row.api_upstream_url,
            rewrite_mode=str(row.rewrite_mode),
            is_published=bool(row.is_published),
            published_at=row.published_at,
            binding_active=bool(row.is_active),
            status=status,
            issue_summary=_gateway_issue(row),
        )

    @staticmethod
    def _dependency_out(
        *,
        row: AppRegistryDependency,
        app_by_code: dict[str, AppRegistryApp],
    ) -> SystemMonitoringDependencyOut:
        status = _dependency_status(row)
        return SystemMonitoringDependencyOut(
            dependency_id=int(row.id),
            source_app_code=str(row.source_app_code),
            source_app_name=_app_name(app_by_code, row.source_app_code),
            target_app_code=str(row.target_app_code),
            target_app_name=_app_name(app_by_code, row.target_app_code),
            dependency_type=str(row.dependency_type),
            description=str(row.description),
            is_required=bool(row.is_required),
            dependency_status=str(row.status),
            dependency_active=bool(row.is_active),
            status=status,
            issue_summary=_dependency_issue(row),
        )

    @staticmethod
    def _service_client_out(
        *,
        row: AppRegistryServiceClient,
        app_by_code: dict[str, AppRegistryApp],
    ) -> SystemMonitoringServiceClientOut:
        active = bool(row.is_active)
        return SystemMonitoringServiceClientOut(
            client_id=int(row.id),
            app_code=str(row.app_code),
            app_name=_app_name(app_by_code, row.app_code),
            client_code=str(row.client_code),
            client_name=str(row.client_name),
            auth_type=str(row.auth_type),
            secret_ref=row.secret_ref,
            client_active=active,
            status=_active_status(active),
            issue_summary=_active_issue(active, "Service Client"),
        )

    @staticmethod
    def _service_permission_out(
        *,
        row: AppRegistryServicePermission,
        app_by_code: dict[str, AppRegistryApp],
        client_by_id: dict[int, AppRegistryServiceClient],
    ) -> SystemMonitoringServicePermissionOut:
        active = bool(row.is_active)
        client = client_by_id.get(int(row.client_id))
        return SystemMonitoringServicePermissionOut(
            permission_id=int(row.id),
            client_id=int(row.client_id),
            client_code=str(client.client_code) if client is not None else None,
            source_app_code=str(row.source_app_code),
            source_app_name=_app_name(app_by_code, row.source_app_code),
            target_app_code=str(row.target_app_code),
            target_app_name=_app_name(app_by_code, row.target_app_code),
            permission_code=str(row.permission_code),
            description=str(row.description),
            permission_active=active,
            status=_active_status(active),
            issue_summary=_active_issue(active, "Service Permission"),
        )

    @staticmethod
    def _openapi_out(
        *,
        row: AppRegistryOpenApiSource,
        app_by_code: dict[str, AppRegistryApp],
        endpoint_by_id: dict[int, AppRegistryEndpoint],
    ) -> SystemMonitoringOpenApiSourceOut:
        endpoint = endpoint_by_id.get(int(row.endpoint_id))
        status = _openapi_status(row)
        return SystemMonitoringOpenApiSourceOut(
            source_id=int(row.id),
            app_code=str(row.app_code),
            app_name=_app_name(app_by_code, row.app_code),
            env_code=str(row.env_code),
            endpoint_id=int(row.endpoint_id),
            endpoint_url=str(endpoint.url) if endpoint is not None else None,
            openapi_url=str(row.openapi_url),
            last_fetched_at=row.last_fetched_at,
            last_checksum=row.last_checksum,
            last_status=str(row.last_status),
            source_active=bool(row.is_active),
            status=status,
            issue_summary=_openapi_issue(row),
        )

    @staticmethod
    def _health_out(
        *,
        row: AppRegistryHealthCheck,
        app_by_code: dict[str, AppRegistryApp],
        endpoint_by_id: dict[int, AppRegistryEndpoint],
        latest_run_by_check_id: dict[int, AppRegistryHealthCheckRun],
    ) -> SystemMonitoringHealthCheckOut:
        endpoint = endpoint_by_id.get(int(row.endpoint_id))
        latest_run = latest_run_by_check_id.get(int(row.id))
        status = _health_status(endpoint=endpoint, check=row, run=latest_run)

        return SystemMonitoringHealthCheckOut(
            health_check_id=int(row.id),
            app_code=str(row.app_code),
            app_name=_app_name(app_by_code, row.app_code),
            env_code=str(row.env_code),
            endpoint_id=int(row.endpoint_id),
            endpoint_type=str(endpoint.endpoint_type) if endpoint is not None else None,
            endpoint_name=str(endpoint.name) if endpoint is not None else None,
            endpoint_url=str(endpoint.url) if endpoint is not None else None,
            check_type=str(row.check_type),
            expected_status=int(row.expected_status),
            timeout_ms=int(row.timeout_ms),
            interval_seconds=int(row.interval_seconds),
            severity=str(row.severity),
            check_active=bool(row.is_active),
            endpoint_active=bool(endpoint.is_active) if endpoint is not None else False,
            status=status,
            http_status=latest_run.http_status if latest_run is not None else None,
            latency_ms=latest_run.latency_ms if latest_run is not None else None,
            latest_checked_at=_latest_checked_at(latest_run),
            issue_summary=_health_issue(
                endpoint=endpoint,
                check=row,
                run=latest_run,
                status=status,
            ),
        )


__all__ = ["SystemMonitoringRemainingService"]
