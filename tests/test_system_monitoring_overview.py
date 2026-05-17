from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from app.main import app
from app.system_monitoring.contracts.system_monitoring_contracts import (
    SystemMonitoringOverviewOut,
)
from app.system_monitoring.services.system_monitoring_service import (
    SystemMonitoringService,
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


def test_system_monitoring_overview_route_is_mounted() -> None:
    assert ("GET", "/admin/system-monitoring/overview") in _method_paths()


def test_system_monitoring_overview_contract_shape() -> None:
    payload = SystemMonitoringOverviewOut.model_validate(
        {
            "summary": {
                "app_count": 1,
                "normal_count": 1,
                "warning_count": 0,
                "error_count": 0,
                "unchecked_count": 0,
            },
            "apps": [
                {
                    "app_code": "wms",
                    "app_name": "WMS 仓储执行系统",
                    "app_status": "ready",
                    "is_active": True,
                    "web_path": "/wms",
                    "api_path": "/api/wms",
                    "gateway_status": "ok",
                    "api_health_status": "ok",
                    "db_health_status": "ok",
                    "openapi_status": "ok",
                    "service_auth_status": "ok",
                    "dependency_status": "ok",
                    "overall_status": "ok",
                    "latest_checked_at": datetime.now(UTC),
                    "issue_summary": None,
                }
            ],
        }
    )

    assert payload.summary.app_count == 1
    assert payload.apps[0].app_code == "wms"
    assert payload.apps[0].overall_status == "ok"


def test_system_monitoring_service_builds_overview_from_registry_rows() -> None:
    checked_at = datetime.now(UTC)

    app_row = SimpleNamespace(
        code="wms",
        name="WMS 仓储执行系统",
        status="ready",
        is_active=True,
        web_path="/wms",
        api_path="/api/wms",
    )
    health_endpoint = SimpleNamespace(
        id=1,
        app_code="wms",
        env_code="local",
        endpoint_type="health",
        name="Health",
        method="GET",
        url="http://127.0.0.1:8000/healthz",
        is_active=True,
    )
    db_endpoint = SimpleNamespace(
        id=2,
        app_code="wms",
        env_code="local",
        endpoint_type="db_health",
        name="DB Health",
        method="GET",
        url="http://127.0.0.1:8000/health/db",
        is_active=True,
    )
    health_check = SimpleNamespace(
        id=11,
        app_code="wms",
        env_code="local",
        endpoint_id=1,
        check_type="http_status",
        is_active=True,
    )
    db_health_check = SimpleNamespace(
        id=12,
        app_code="wms",
        env_code="local",
        endpoint_id=2,
        check_type="http_status",
        is_active=True,
    )
    health_run = SimpleNamespace(
        id=21,
        health_check_id=11,
        started_at=checked_at,
        finished_at=checked_at,
        status="success",
    )
    db_health_run = SimpleNamespace(
        id=22,
        health_check_id=12,
        started_at=checked_at,
        finished_at=checked_at,
        status="success",
    )

    class FakeRepo:
        def list_apps(self) -> list[object]:
            return [app_row]

        def list_endpoints(self) -> list[object]:
            return [health_endpoint, db_endpoint]

        def list_databases(self) -> list[object]:
            return []

        def list_gateway_bindings(self) -> list[object]:
            return [SimpleNamespace(app_code="wms", is_active=True)]

        def list_dependencies(self) -> list[object]:
            return [
                SimpleNamespace(
                    source_app_code="wms",
                    target_app_code="pms",
                    status="ready",
                    is_active=True,
                )
            ]

        def list_service_clients(self) -> list[object]:
            return [SimpleNamespace(app_code="wms", is_active=True)]

        def list_service_permissions(self) -> list[object]:
            return [
                SimpleNamespace(
                    source_app_code="wms",
                    target_app_code="pms",
                    is_active=True,
                )
            ]

        def list_health_checks(self) -> list[object]:
            return [health_check, db_health_check]

        def list_latest_health_check_runs(self, health_check_ids: set[int]) -> list[object]:
            return [health_run, db_health_run]

        def list_openapi_sources(self) -> list[object]:
            return [SimpleNamespace(app_code="wms", last_status="success", is_active=True)]

    service = object.__new__(SystemMonitoringService)
    service.repo = FakeRepo()

    overview = service.get_overview()

    assert overview.summary.app_count == 1
    assert overview.summary.normal_count == 1
    assert overview.apps[0].app_code == "wms"
    assert overview.apps[0].overall_status == "ok"
    assert overview.apps[0].latest_checked_at == checked_at
    assert overview.apps[0].issue_summary is None
