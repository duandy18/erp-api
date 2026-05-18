from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryServicePermissionWriteRun,
)
from app.db.base import Base
from app.main import app
from app.system_service_auth.contracts.system_service_auth_write_status_contracts import (
    SystemServiceAuthWriteStatusListOut,
)
from app.system_service_auth.services.system_service_auth_write_status_service import (
    SystemServiceAuthWriteStatusService,
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


def test_service_auth_write_run_model_and_migration_are_registered() -> None:
    migration = Path("alembic/versions/0018_service_auth_write_status.py").read_text()

    assert AppRegistryServicePermissionWriteRun.__table__.name == (
        "app_registry_service_permission_write_runs"
    )
    assert "app_registry_service_permission_write_runs" in set(Base.metadata.tables)
    assert "app_registry_service_permission_write_runs" in migration
    assert "0018_service_auth_write_status" in migration
    assert "0017_system_child_pages" in migration


def test_system_service_auth_write_status_route_is_mounted() -> None:
    assert ("GET", "/admin/system-service-auth/write-status") in _method_paths()


def test_system_service_auth_write_status_contract_shape() -> None:
    now = datetime.now(UTC)
    payload = SystemServiceAuthWriteStatusListOut.model_validate(
        {
            "items": [
                {
                    "permission_id": 1,
                    "client_id": 1,
                    "client_code": "wms-service",
                    "source_app_code": "wms",
                    "source_app_name": "WMS 仓储执行系统",
                    "target_app_code": "pms",
                    "target_app_name": "PMS 商品主数据系统",
                    "permission_code": "pms.read.items",
                    "description": "WMS 读取 PMS 商品主数据",
                    "permission_active": True,
                    "latest_run": None,
                }
            ],
            "recent_runs": [
                {
                    "run_id": 1,
                    "permission_id": 1,
                    "source_app_code": "wms",
                    "target_app_code": "pms",
                    "client_code": "wms-service",
                    "permission_code": "pms.read.items",
                    "operation": "upsert",
                    "status": "success",
                    "started_at": now,
                    "finished_at": now,
                    "target_base_url": "http://127.0.0.1:8002",
                    "http_status": 200,
                    "error_message": None,
                    "raw_excerpt": None,
                }
            ],
        }
    )

    assert payload.items[0].permission_code == "pms.read.items"
    assert payload.items[0].latest_run is None
    assert payload.recent_runs[0].status == "success"


def test_system_service_auth_write_status_service_builds_latest_run() -> None:
    now = datetime.now(UTC)

    app_wms = SimpleNamespace(code="wms", name="WMS 仓储执行系统", sort_order=10)
    app_pms = SimpleNamespace(code="pms", name="PMS 商品主数据系统", sort_order=20)
    client = SimpleNamespace(id=1, app_code="wms", client_code="wms-service")
    permission = SimpleNamespace(
        id=1,
        client_id=1,
        source_app_code="wms",
        target_app_code="pms",
        permission_code="pms.read.items",
        description="WMS 读取 PMS 商品主数据",
        is_active=True,
    )
    run = SimpleNamespace(
        id=8,
        permission_id=1,
        source_app_code="wms",
        target_app_code="pms",
        client_code="wms-service",
        permission_code="pms.read.items",
        operation="upsert",
        status="failure",
        started_at=now,
        finished_at=now,
        target_base_url="http://127.0.0.1:8002",
        http_status=500,
        error_message="target failed",
        raw_excerpt="error",
    )

    class FakeRepo:
        def list_apps(self) -> list[object]:
            return [app_wms, app_pms]

        def list_clients(self) -> list[object]:
            return [client]

        def list_permissions(self) -> list[object]:
            return [permission]

        def list_latest_write_runs(self, permission_ids: set[int]) -> list[object]:
            return [run]

        def list_recent_write_runs(self, *, limit: int = 100) -> list[object]:
            return [run]

    service = SystemServiceAuthWriteStatusService(
        SimpleNamespace(),
        repository=FakeRepo(),  # type: ignore[arg-type]
    )

    payload = service.list_write_status()

    assert payload.items[0].latest_run is not None
    assert payload.items[0].latest_run.status == "failure"
    assert payload.items[0].latest_run.http_status == 500
    assert payload.recent_runs[0].run_id == 8


def test_service_auth_write_status_identifier_names_fit_postgres_limit() -> None:
    migration = Path("alembic/versions/0018_service_auth_write_status.py").read_text()
    names = (
        "ck_svc_perm_write_runs_operation",
        "ck_svc_perm_write_runs_status",
        "ck_svc_perm_write_runs_source",
        "ck_svc_perm_write_runs_target",
        "ck_svc_perm_write_runs_permission",
        "ck_svc_perm_write_runs_http_status",
    )

    for name in names:
        assert name in migration
        assert len(name) <= 63
