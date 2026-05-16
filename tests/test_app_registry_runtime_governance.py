from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from app.app_registry.contracts.app_registry_app_metadata_contracts import (
    AppRegistryAppMetadataOut,
)
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryHealthCheck,
    AppRegistryHealthCheckRun,
    AppRegistryOpenApiSource,
)
from app.db.base import Base


def test_app_registry_runtime_governance_models_are_registered() -> None:
    assert AppRegistryHealthCheck.__table__.name == "app_registry_health_checks"
    assert AppRegistryHealthCheckRun.__table__.name == "app_registry_health_check_runs"
    assert AppRegistryOpenApiSource.__table__.name == "app_registry_openapi_sources"

    assert "app_registry_health_checks" in set(Base.metadata.tables)
    assert "app_registry_health_check_runs" in set(Base.metadata.tables)
    assert "app_registry_openapi_sources" in set(Base.metadata.tables)


def test_app_registry_profile_contract_includes_runtime_governance() -> None:
    started_at = datetime.now(UTC)
    finished_at = datetime.now(UTC)

    payload = AppRegistryAppMetadataOut.model_validate(
        {
            "app": {
                "code": "wms",
                "name": "WMS 仓储执行系统",
                "description": "库存、入库、出库、仓内执行。",
                "web_path": "/wms",
                "api_path": "/api/wms",
                "local_web_url": "http://127.0.0.1:5173",
                "local_api_url": "http://127.0.0.1:8000",
                "status": "ready",
                "domain_code": "wms",
                "app_type": "business",
                "owner_name": None,
                "owner_contact": None,
                "sort_order": 10,
                "is_active": True,
            },
            "health_checks": [
                {
                    "id": 1,
                    "app_code": "wms",
                    "env_code": "local",
                    "endpoint_id": 8,
                    "check_type": "http_status",
                    "expected_status": 200,
                    "expected_json_path": None,
                    "expected_json_value": None,
                    "timeout_ms": 5000,
                    "interval_seconds": 60,
                    "severity": "critical",
                    "is_active": True,
                    "latest_run": {
                        "id": 10,
                        "health_check_id": 1,
                        "started_at": started_at,
                        "finished_at": finished_at,
                        "status": "success",
                        "http_status": 200,
                        "latency_ms": 18,
                        "message": "HTTP status matched expected status 200",
                        "raw_excerpt": '{"status":"ok"}',
                    },
                }
            ],
            "openapi_sources": [
                {
                    "id": 1,
                    "app_code": "wms",
                    "env_code": "local",
                    "endpoint_id": 10,
                    "openapi_url": "http://127.0.0.1:8000/openapi.json",
                    "last_fetched_at": None,
                    "last_checksum": None,
                    "last_status": "unknown",
                    "is_active": True,
                }
            ],
        }
    )

    assert payload.health_checks[0].check_type == "http_status"
    assert payload.health_checks[0].expected_status == 200
    assert payload.health_checks[0].latest_run is not None
    assert payload.health_checks[0].latest_run.status == "success"
    assert payload.openapi_sources[0].last_status == "unknown"


def test_app_registry_profile_contract_defaults_latest_run_to_none() -> None:
    payload = AppRegistryAppMetadataOut.model_validate(
        {
            "app": {
                "code": "wms",
                "name": "WMS 仓储执行系统",
                "description": "库存、入库、出库、仓内执行。",
                "web_path": "/wms",
                "api_path": "/api/wms",
                "local_web_url": "http://127.0.0.1:5173",
                "local_api_url": "http://127.0.0.1:8000",
                "status": "ready",
                "domain_code": "wms",
                "app_type": "business",
                "owner_name": None,
                "owner_contact": None,
                "sort_order": 10,
                "is_active": True,
            },
            "health_checks": [
                {
                    "id": 1,
                    "app_code": "wms",
                    "env_code": "local",
                    "endpoint_id": 8,
                    "check_type": "http_status",
                    "expected_status": 200,
                    "expected_json_path": None,
                    "expected_json_value": None,
                    "timeout_ms": 5000,
                    "interval_seconds": 60,
                    "severity": "critical",
                    "is_active": True,
                }
            ],
            "openapi_sources": [],
        }
    )

    assert payload.health_checks[0].latest_run is None


def test_app_registry_runtime_governance_migration_contains_tables_and_seed() -> None:
    migration = Path("alembic/versions/0009_app_registry_runtime_governance.py").read_text()

    assert "app_registry_health_checks" in migration
    assert "app_registry_health_check_runs" in migration
    assert "app_registry_openapi_sources" in migration
    assert "endpoint_type IN ('health', 'db_health')" in migration
    assert "endpoint_type = 'openapi'" in migration
    assert "DATABASE_URL" not in migration


def test_app_registry_app_metadata_service_maps_runtime_governance_fields() -> None:
    from app.app_registry.services.app_registry_app_metadata_service import (
        AppRegistryAppMetadataService,
    )

    app = SimpleNamespace(
        code="wms",
        name="WMS 仓储执行系统",
        description="库存、入库、出库、仓内执行。",
        web_path="/wms",
        api_path="/api/wms",
        local_web_url="http://127.0.0.1:5173",
        local_api_url="http://127.0.0.1:8000",
        status="ready",
        domain_code="wms",
        app_type="business",
        owner_name=None,
        owner_contact=None,
        sort_order=10,
        is_active=True,
    )
    health_check = SimpleNamespace(
        id=1,
        app_code="wms",
        env_code="local",
        endpoint_id=8,
        check_type="http_status",
        expected_status=200,
        expected_json_path=None,
        expected_json_value=None,
        timeout_ms=5000,
        interval_seconds=60,
        severity="critical",
        is_active=True,
    )
    latest_run = SimpleNamespace(
        id=100,
        health_check_id=1,
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        status="success",
        http_status=200,
        latency_ms=18,
        message="HTTP status matched expected status 200",
        raw_excerpt='{"status":"ok"}',
    )
    openapi_source = SimpleNamespace(
        id=1,
        app_code="wms",
        env_code="local",
        endpoint_id=10,
        openapi_url="http://127.0.0.1:8000/openapi.json",
        last_fetched_at=None,
        last_checksum=None,
        last_status="unknown",
        is_active=True,
    )

    class FakeRepo:
        def list_app_environments(self, app_code: str) -> list[object]:
            return []

        def list_service_clients(self, app_code: str) -> list[object]:
            return []

        def list_service_permissions(self, app_code: str) -> list[object]:
            return []

        def list_service_clients_by_ids(self, client_ids: set[int]) -> list[object]:
            return []

        def list_components(self, app_code: str) -> list[object]:
            return []

        def list_environments(self, env_codes: set[str]) -> list[object]:
            return []

        def list_endpoints(self, app_code: str) -> list[object]:
            return []

        def list_databases(self, app_code: str) -> list[object]:
            return []

        def list_repositories(self, app_code: str) -> list[object]:
            return []

        def list_gateway_bindings(self, app_code: str) -> list[object]:
            return []

        def list_outgoing_dependencies(self, app_code: str) -> list[object]:
            return []

        def list_incoming_dependencies(self, app_code: str) -> list[object]:
            return []

        def list_health_checks(self, app_code: str) -> list[object]:
            return [health_check]

        def list_latest_health_check_runs(self, health_check_ids: set[int]) -> list[object]:
            return [latest_run]

        def list_openapi_sources(self, app_code: str) -> list[object]:
            return [openapi_source]

    service = object.__new__(AppRegistryAppMetadataService)
    service.repo = FakeRepo()

    profile = service._build_profile(app)

    assert len(profile.health_checks) == 1
    assert len(profile.openapi_sources) == 1
    assert profile.health_checks[0].endpoint_id == 8
    assert profile.health_checks[0].latest_run is not None
    assert profile.health_checks[0].latest_run.status == "success"
    assert profile.health_checks[0].latest_run.http_status == 200
    assert profile.openapi_sources[0].last_status == "unknown"


def test_app_registry_app_metadata_service_uses_latest_run_by_started_at_then_id() -> None:
    from app.app_registry.services.app_registry_app_metadata_service import (
        AppRegistryAppMetadataService,
    )

    app = SimpleNamespace(
        code="wms",
        name="WMS 仓储执行系统",
        description="库存、入库、出库、仓内执行。",
        web_path="/wms",
        api_path="/api/wms",
        local_web_url="http://127.0.0.1:5173",
        local_api_url="http://127.0.0.1:8000",
        status="ready",
        domain_code="wms",
        app_type="business",
        owner_name=None,
        owner_contact=None,
        sort_order=10,
        is_active=True,
    )
    health_check = SimpleNamespace(
        id=1,
        app_code="wms",
        env_code="local",
        endpoint_id=8,
        check_type="http_status",
        expected_status=200,
        expected_json_path=None,
        expected_json_value=None,
        timeout_ms=5000,
        interval_seconds=60,
        severity="critical",
        is_active=True,
    )
    older_run = SimpleNamespace(
        id=10,
        health_check_id=1,
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        finished_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="failure",
        http_status=503,
        latency_ms=100,
        message="older",
        raw_excerpt=None,
    )
    latest_run = SimpleNamespace(
        id=11,
        health_check_id=1,
        started_at=datetime(2026, 1, 2, tzinfo=UTC),
        finished_at=datetime(2026, 1, 2, tzinfo=UTC),
        status="success",
        http_status=200,
        latency_ms=18,
        message="latest",
        raw_excerpt=None,
    )

    class FakeRepo:
        def list_app_environments(self, app_code: str) -> list[object]:
            return []

        def list_service_clients(self, app_code: str) -> list[object]:
            return []

        def list_service_permissions(self, app_code: str) -> list[object]:
            return []

        def list_service_clients_by_ids(self, client_ids: set[int]) -> list[object]:
            return []

        def list_components(self, app_code: str) -> list[object]:
            return []

        def list_environments(self, env_codes: set[str]) -> list[object]:
            return []

        def list_endpoints(self, app_code: str) -> list[object]:
            return []

        def list_databases(self, app_code: str) -> list[object]:
            return []

        def list_repositories(self, app_code: str) -> list[object]:
            return []

        def list_gateway_bindings(self, app_code: str) -> list[object]:
            return []

        def list_outgoing_dependencies(self, app_code: str) -> list[object]:
            return []

        def list_incoming_dependencies(self, app_code: str) -> list[object]:
            return []

        def list_health_checks(self, app_code: str) -> list[object]:
            return [health_check]

        def list_latest_health_check_runs(self, health_check_ids: set[int]) -> list[object]:
            return [latest_run, older_run]

        def list_openapi_sources(self, app_code: str) -> list[object]:
            return []

    service = object.__new__(AppRegistryAppMetadataService)
    service.repo = FakeRepo()

    profile = service._build_profile(app)

    assert profile.health_checks[0].latest_run is not None
    assert profile.health_checks[0].latest_run.id == 11
    assert profile.health_checks[0].latest_run.message == "latest"
