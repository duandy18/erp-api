from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from app.main import app
from app.system_monitoring.contracts.system_monitoring_endpoint_contracts import (
    SystemMonitoringEndpointStatusListOut,
)
from app.system_monitoring.services.system_monitoring_endpoint_service import (
    SystemMonitoringEndpointService,
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


def test_system_monitoring_endpoints_route_is_mounted() -> None:
    assert ("GET", "/admin/system-monitoring/endpoints") in _method_paths()


def test_system_monitoring_endpoint_status_contract_shape() -> None:
    payload = SystemMonitoringEndpointStatusListOut.model_validate(
        {
            "endpoints": [
                {
                    "app_code": "wms",
                    "app_name": "WMS 仓储执行系统",
                    "env_code": "local",
                    "api_endpoint_id": 1,
                    "health_endpoint_id": 2,
                    "api_url": "http://127.0.0.1:8000",
                    "health_url": "http://127.0.0.1:8000/healthz",
                    "api_endpoint_active": True,
                    "health_endpoint_active": True,
                    "health_check_id": 11,
                    "status": "ok",
                    "http_status": 200,
                    "latency_ms": 12,
                    "latest_checked_at": datetime.now(UTC),
                    "issue_summary": None,
                }
            ]
        }
    )

    assert payload.endpoints[0].app_code == "wms"
    assert payload.endpoints[0].status == "ok"


def test_system_monitoring_endpoint_service_builds_rows() -> None:
    checked_at = datetime.now(UTC)

    app_row = SimpleNamespace(
        code="wms",
        name="WMS 仓储执行系统",
    )
    api_endpoint = SimpleNamespace(
        id=1,
        app_code="wms",
        env_code="local",
        endpoint_type="api",
        url="http://127.0.0.1:8000",
        is_active=True,
    )
    health_endpoint = SimpleNamespace(
        id=2,
        app_code="wms",
        env_code="local",
        endpoint_type="health",
        url="http://127.0.0.1:8000/healthz",
        is_active=True,
    )
    health_check = SimpleNamespace(
        id=11,
        app_code="wms",
        endpoint_id=2,
        is_active=True,
    )
    latest_run = SimpleNamespace(
        id=21,
        health_check_id=11,
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

        def list_endpoints(self) -> list[object]:
            return [api_endpoint, health_endpoint]

        def list_health_checks(self) -> list[object]:
            return [health_check]

        def list_latest_health_check_runs(self, health_check_ids: set[int]) -> list[object]:
            return [latest_run]

    service = object.__new__(SystemMonitoringEndpointService)
    service.repo = FakeRepo()

    payload = service.list_endpoint_statuses()

    assert len(payload.endpoints) == 1
    assert payload.endpoints[0].app_code == "wms"
    assert payload.endpoints[0].status == "ok"
    assert payload.endpoints[0].http_status == 200
    assert payload.endpoints[0].latest_checked_at == checked_at
    assert payload.endpoints[0].issue_summary is None
