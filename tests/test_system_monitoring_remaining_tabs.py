from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from app.main import app
from app.system_monitoring.contracts.system_monitoring_remaining_contracts import (
    SystemMonitoringDependencyListOut,
    SystemMonitoringGatewayBindingListOut,
    SystemMonitoringHealthCheckListOut,
    SystemMonitoringOpenApiSourceListOut,
    SystemMonitoringServiceAuthOut,
)
from app.system_monitoring.services.system_monitoring_remaining_service import (
    SystemMonitoringRemainingService,
)


def _method_paths() -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", None) or []
        for method in methods:
            if method in {"GET", "POST", "PATCH", "PUT", "DELETE"}:
                pairs.add((method, path))
    return pairs


def test_system_monitoring_remaining_routes_are_mounted() -> None:
    pairs = _method_paths()

    assert ("GET", "/admin/system-monitoring/gateway") in pairs
    assert ("GET", "/admin/system-monitoring/dependencies") in pairs
    assert ("GET", "/admin/system-monitoring/service-auth") in pairs
    assert ("GET", "/admin/system-monitoring/openapi") in pairs
    assert ("GET", "/admin/system-monitoring/health") in pairs


def test_system_monitoring_gateway_contract_shape() -> None:
    payload = SystemMonitoringGatewayBindingListOut.model_validate(
        {
            "gateway_bindings": [
                {
                    "binding_id": 1,
                    "app_code": "wms",
                    "app_name": "WMS 仓储执行系统",
                    "env_code": "local",
                    "web_path": "/wms",
                    "api_path": "/api/wms",
                    "web_upstream_url": "http://host.docker.internal:5173",
                    "api_upstream_url": "http://host.docker.internal:8000",
                    "rewrite_mode": "preserve_prefix",
                    "is_published": True,
                    "published_at": datetime.now(UTC),
                    "binding_active": True,
                    "status": "ok",
                    "issue_summary": None,
                }
            ]
        }
    )

    assert payload.gateway_bindings[0].app_code == "wms"
    assert payload.gateway_bindings[0].status == "ok"


def test_system_monitoring_dependency_contract_shape() -> None:
    payload = SystemMonitoringDependencyListOut.model_validate(
        {
            "dependencies": [
                {
                    "dependency_id": 1,
                    "source_app_code": "wms",
                    "source_app_name": "WMS 仓储执行系统",
                    "target_app_code": "pms",
                    "target_app_name": "PMS 商品主数据系统",
                    "dependency_type": "projection_feed",
                    "description": "WMS 读取 PMS 商品主数据。",
                    "is_required": True,
                    "dependency_status": "ready",
                    "dependency_active": True,
                    "status": "ok",
                    "issue_summary": None,
                }
            ]
        }
    )

    assert payload.dependencies[0].source_app_code == "wms"
    assert payload.dependencies[0].status == "ok"


def test_system_monitoring_service_auth_contract_shape() -> None:
    payload = SystemMonitoringServiceAuthOut.model_validate(
        {
            "clients": [
                {
                    "client_id": 1,
                    "app_code": "wms",
                    "app_name": "WMS 仓储执行系统",
                    "client_code": "wms-service",
                    "client_name": "WMS Service Client",
                    "auth_type": "none",
                    "secret_ref": None,
                    "client_active": True,
                    "status": "ok",
                    "issue_summary": None,
                }
            ],
            "permissions": [
                {
                    "permission_id": 1,
                    "client_id": 1,
                    "client_code": "wms-service",
                    "source_app_code": "wms",
                    "source_app_name": "WMS 仓储执行系统",
                    "target_app_code": "pms",
                    "target_app_name": "PMS 商品主数据系统",
                    "permission_code": "pms.read.items",
                    "description": "WMS 读取 PMS 商品主数据。",
                    "permission_active": True,
                    "status": "ok",
                    "issue_summary": None,
                }
            ],
        }
    )

    assert payload.clients[0].client_code == "wms-service"
    assert payload.permissions[0].permission_code == "pms.read.items"


def test_system_monitoring_openapi_contract_shape() -> None:
    payload = SystemMonitoringOpenApiSourceListOut.model_validate(
        {
            "openapi_sources": [
                {
                    "source_id": 1,
                    "app_code": "wms",
                    "app_name": "WMS 仓储执行系统",
                    "env_code": "local",
                    "endpoint_id": 10,
                    "endpoint_url": "http://127.0.0.1:8000/openapi.json",
                    "openapi_url": "http://127.0.0.1:8000/openapi.json",
                    "last_fetched_at": datetime.now(UTC),
                    "last_checksum": "abc",
                    "last_status": "success",
                    "source_active": True,
                    "status": "ok",
                    "issue_summary": None,
                }
            ]
        }
    )

    assert payload.openapi_sources[0].app_code == "wms"
    assert payload.openapi_sources[0].status == "ok"


def test_system_monitoring_health_contract_shape() -> None:
    payload = SystemMonitoringHealthCheckListOut.model_validate(
        {
            "health_checks": [
                {
                    "health_check_id": 1,
                    "app_code": "wms",
                    "app_name": "WMS 仓储执行系统",
                    "env_code": "local",
                    "endpoint_id": 8,
                    "endpoint_type": "health",
                    "endpoint_name": "Health",
                    "endpoint_url": "http://127.0.0.1:8000/healthz",
                    "check_type": "http_status",
                    "expected_status": 200,
                    "timeout_ms": 5000,
                    "interval_seconds": 60,
                    "severity": "critical",
                    "check_active": True,
                    "endpoint_active": True,
                    "status": "ok",
                    "http_status": 200,
                    "latency_ms": 12,
                    "latest_checked_at": datetime.now(UTC),
                    "issue_summary": None,
                }
            ]
        }
    )

    assert payload.health_checks[0].app_code == "wms"
    assert payload.health_checks[0].status == "ok"


def test_system_monitoring_remaining_service_builds_rows() -> None:
    checked_at = datetime.now(UTC)

    app_row = SimpleNamespace(code="wms", name="WMS 仓储执行系统")
    gateway_row = SimpleNamespace(
        id=1,
        app_code="wms",
        env_code="local",
        web_path="/wms",
        api_path="/api/wms",
        web_upstream_url="http://host.docker.internal:5173",
        api_upstream_url="http://host.docker.internal:8000",
        rewrite_mode="preserve_prefix",
        is_published=True,
        published_at=checked_at,
        is_active=True,
    )
    dependency_row = SimpleNamespace(
        id=1,
        source_app_code="wms",
        target_app_code="wms",
        dependency_type="http_api",
        description="self check",
        is_required=True,
        status="ready",
        is_active=True,
    )
    service_client_row = SimpleNamespace(
        id=1,
        app_code="wms",
        client_code="wms-service",
        client_name="WMS Service Client",
        auth_type="none",
        secret_ref=None,
        is_active=True,
    )
    service_permission_row = SimpleNamespace(
        id=1,
        client_id=1,
        source_app_code="wms",
        target_app_code="wms",
        permission_code="wms.read.self",
        description="self check",
        is_active=True,
    )
    endpoint_row = SimpleNamespace(
        id=8,
        app_code="wms",
        env_code="local",
        endpoint_type="health",
        name="Health",
        url="http://127.0.0.1:8000/healthz",
        is_active=True,
    )
    openapi_source_row = SimpleNamespace(
        id=1,
        app_code="wms",
        env_code="local",
        endpoint_id=8,
        openapi_url="http://127.0.0.1:8000/openapi.json",
        last_fetched_at=checked_at,
        last_checksum="abc",
        last_status="success",
        is_active=True,
    )
    health_check_row = SimpleNamespace(
        id=1,
        app_code="wms",
        env_code="local",
        endpoint_id=8,
        check_type="http_status",
        expected_status=200,
        timeout_ms=5000,
        interval_seconds=60,
        severity="critical",
        is_active=True,
    )
    latest_run = SimpleNamespace(
        id=1,
        health_check_id=1,
        started_at=checked_at,
        finished_at=checked_at,
        status="success",
        http_status=200,
        latency_ms=12,
        message="HTTP status matched expected status 200",
    )

    class FakeRepo:
        def list_apps(self) -> list[object]:
            return [app_row]

        def list_gateway_bindings(self) -> list[object]:
            return [gateway_row]

        def list_dependencies(self) -> list[object]:
            return [dependency_row]

        def list_service_clients(self) -> list[object]:
            return [service_client_row]

        def list_service_permissions(self) -> list[object]:
            return [service_permission_row]

        def list_endpoints(self) -> list[object]:
            return [endpoint_row]

        def list_openapi_sources(self) -> list[object]:
            return [openapi_source_row]

        def list_health_checks(self) -> list[object]:
            return [health_check_row]

        def list_latest_health_check_runs(self, health_check_ids: set[int]) -> list[object]:
            return [latest_run]

    service = object.__new__(SystemMonitoringRemainingService)
    service.repo = FakeRepo()

    assert service.list_gateway_bindings().gateway_bindings[0].status == "ok"
    assert service.list_dependencies().dependencies[0].status == "ok"
    assert service.list_service_auth().clients[0].status == "ok"
    assert service.list_service_auth().permissions[0].status == "ok"
    assert service.list_openapi_sources().openapi_sources[0].status == "ok"
    assert service.list_health_checks().health_checks[0].status == "ok"
