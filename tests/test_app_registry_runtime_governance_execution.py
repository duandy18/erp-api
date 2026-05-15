from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from app.app_registry.contracts.app_registry_runtime_governance_contracts import (
    AppRegistryHealthCheckRunOut,
)
from app.app_registry.services.app_registry_runtime_governance_service import (
    AppRegistryRuntimeGovernanceService,
    HttpStatusProbeResult,
)
from app.main import app


def _method_paths() -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", None) or []
        for method in methods:
            if method in {"GET", "POST", "PATCH", "PUT", "DELETE"}:
                pairs.add((method, path))
    return pairs


def test_app_registry_health_check_run_route_is_mounted() -> None:
    pairs = _method_paths()

    assert ("POST", "/admin/app-registry/health-checks/{health_check_id}/run") in pairs


def test_app_registry_health_check_run_contract_shape() -> None:
    payload = AppRegistryHealthCheckRunOut.model_validate(
        {
            "id": 1,
            "health_check_id": 1,
            "started_at": datetime.now(UTC),
            "finished_at": datetime.now(UTC),
            "status": "success",
            "http_status": 200,
            "latency_ms": 12,
            "message": "HTTP status matched expected status 200",
            "raw_excerpt": '{"status":"ok"}',
        }
    )

    assert payload.health_check_id == 1
    assert payload.status == "success"
    assert payload.http_status == 200


def test_app_registry_health_check_run_service_records_success() -> None:
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
    endpoint = SimpleNamespace(
        id=8,
        app_code="wms",
        env_code="local",
        endpoint_type="health",
        method="GET",
        path="/healthz",
        url="http://127.0.0.1:8000/healthz",
        timeout_ms=5000,
        is_active=True,
    )

    class FakeRepo:
        saved_row: object | None = None

        def get_health_check(self, health_check_id: int) -> object:
            return health_check

        def get_endpoint(self, endpoint_id: int) -> object:
            return endpoint

        def create_health_check_run(self, row: object) -> object:
            self.saved_row = row
            row.id = 99
            return row

    fake_repo = FakeRepo()

    service = object.__new__(AppRegistryRuntimeGovernanceService)
    service.repo = fake_repo
    service.http_status_probe = lambda url, timeout: HttpStatusProbeResult(
        http_status=200,
        raw_excerpt='{"status":"ok"}',
    )

    result = service.run_health_check_once(1)

    assert result.id == 99
    assert result.health_check_id == 1
    assert result.status == "success"
    assert result.http_status == 200
    assert result.raw_excerpt == '{"status":"ok"}'
    assert fake_repo.saved_row is not None


def test_app_registry_health_check_run_service_records_failure() -> None:
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
    endpoint = SimpleNamespace(
        id=8,
        app_code="wms",
        env_code="local",
        endpoint_type="health",
        method="GET",
        path="/healthz",
        url="http://127.0.0.1:8000/healthz",
        timeout_ms=5000,
        is_active=True,
    )

    class FakeRepo:
        def get_health_check(self, health_check_id: int) -> object:
            return health_check

        def get_endpoint(self, endpoint_id: int) -> object:
            return endpoint

        def create_health_check_run(self, row: object) -> object:
            row.id = 100
            return row

    service = object.__new__(AppRegistryRuntimeGovernanceService)
    service.repo = FakeRepo()
    service.http_status_probe = lambda url, timeout: HttpStatusProbeResult(
        http_status=503,
        raw_excerpt="service unavailable",
    )

    result = service.run_health_check_once(1)

    assert result.id == 100
    assert result.status == "failure"
    assert result.http_status == 503
    assert result.raw_excerpt == "service unavailable"
