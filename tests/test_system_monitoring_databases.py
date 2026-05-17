from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from app.main import app
from app.system_monitoring.contracts.system_monitoring_database_contracts import (
    SystemMonitoringDatabaseStatusListOut,
)
from app.system_monitoring.services.system_monitoring_database_service import (
    SystemMonitoringDatabaseService,
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


def test_system_monitoring_databases_route_is_mounted() -> None:
    assert ("GET", "/admin/system-monitoring/databases") in _method_paths()


def test_system_monitoring_database_status_contract_shape() -> None:
    payload = SystemMonitoringDatabaseStatusListOut.model_validate(
        {
            "databases": [
                {
                    "app_code": "wms",
                    "app_name": "WMS 仓储执行系统",
                    "env_code": "local",
                    "database_id": 1,
                    "db_engine": "postgres",
                    "db_host_label": "127.0.0.1",
                    "db_port": 5433,
                    "db_name": "wms",
                    "schema_name": "public",
                    "migration_tool": "alembic",
                    "migration_command": "make upgrade-dev",
                    "access_policy": "health_endpoint_only",
                    "database_active": True,
                    "health_endpoint_id": 2,
                    "health_url": "http://127.0.0.1:8000/health/db",
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

    assert payload.databases[0].app_code == "wms"
    assert payload.databases[0].status == "ok"


def test_system_monitoring_database_service_builds_rows() -> None:
    checked_at = datetime.now(UTC)

    app_row = SimpleNamespace(
        code="wms",
        name="WMS 仓储执行系统",
    )
    database_row = SimpleNamespace(
        id=1,
        app_code="wms",
        env_code="local",
        db_engine="postgres",
        db_host_label="127.0.0.1",
        db_port=5433,
        db_name="wms",
        schema_name="public",
        migration_tool="alembic",
        migration_command="make upgrade-dev",
        health_endpoint_id=2,
        access_policy="health_endpoint_only",
        is_active=True,
    )
    db_health_endpoint = SimpleNamespace(
        id=2,
        app_code="wms",
        env_code="local",
        endpoint_type="db_health",
        url="http://127.0.0.1:8000/health/db",
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
            return [db_health_endpoint]

        def list_databases(self) -> list[object]:
            return [database_row]

        def list_health_checks(self) -> list[object]:
            return [health_check]

        def list_latest_health_check_runs(self, health_check_ids: set[int]) -> list[object]:
            return [latest_run]

    service = object.__new__(SystemMonitoringDatabaseService)
    service.repo = FakeRepo()

    payload = service.list_database_statuses()

    assert len(payload.databases) == 1
    assert payload.databases[0].app_code == "wms"
    assert payload.databases[0].status == "ok"
    assert payload.databases[0].http_status == 200
    assert payload.databases[0].latest_checked_at == checked_at
    assert payload.databases[0].issue_summary is None
