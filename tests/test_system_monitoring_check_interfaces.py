from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryDependency,
    AppRegistryGatewayBinding,
    AppRegistryOpenApiSource,
    AppRegistryServiceClient,
    AppRegistryServicePermission,
)
from app.main import app
from app.system_monitoring.contracts.system_monitoring_check_contracts import (
    SystemMonitoringCheckResultOut,
)
from app.system_monitoring.services.system_monitoring_check_service import (
    OpenApiFetchResult,
    SystemMonitoringCheckService,
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


def test_system_monitoring_check_routes_are_mounted() -> None:
    pairs = _method_paths()

    assert ("POST", "/admin/system-monitoring/gateway/{binding_id}/check") in pairs
    assert ("POST", "/admin/system-monitoring/dependencies/{dependency_id}/check") in pairs
    assert ("POST", "/admin/system-monitoring/service-auth/clients/{client_id}/check") in pairs
    assert (
        "POST",
        "/admin/system-monitoring/service-auth/permissions/{permission_id}/check",
    ) in pairs
    assert ("POST", "/admin/system-monitoring/openapi/{source_id}/check") in pairs


def test_system_monitoring_check_contract_shape() -> None:
    payload = SystemMonitoringCheckResultOut.model_validate(
        {
            "target_type": "gateway",
            "target_id": 1,
            "status": "ok",
            "checked_at": datetime.now(UTC),
            "message": "Gateway 绑定配置正常",
            "details": {
                "app_code": "wms",
                "web_path": "/wms",
                "is_active": True,
            },
        }
    )

    assert payload.target_type == "gateway"
    assert payload.status == "ok"
    assert payload.details["app_code"] == "wms"


def test_system_monitoring_check_service_checks_gateway_dependency_and_service_auth() -> None:
    app_wms = SimpleNamespace(code="wms", name="WMS 仓储执行系统")
    app_pms = SimpleNamespace(code="pms", name="PMS 商品主数据系统")
    gateway = SimpleNamespace(
        id=1,
        app_code="wms",
        env_code="local",
        web_path="/wms",
        api_path="/api/wms",
        web_upstream_url="http://host.docker.internal:5173",
        api_upstream_url="http://host.docker.internal:8000",
        rewrite_mode="preserve_prefix",
        is_published=True,
        published_at=datetime.now(UTC),
        is_active=True,
    )
    dependency = SimpleNamespace(
        id=1,
        source_app_code="wms",
        target_app_code="pms",
        dependency_type="projection_feed",
        description="WMS 读取 PMS 商品主数据。",
        is_required=True,
        status="ready",
        is_active=True,
    )
    client = SimpleNamespace(
        id=1,
        app_code="wms",
        client_code="wms-service",
        client_name="WMS Service Client",
        auth_type="none",
        secret_ref=None,
        is_active=True,
    )
    permission = SimpleNamespace(
        id=1,
        client_id=1,
        source_app_code="wms",
        target_app_code="pms",
        permission_code="pms.read.items",
        description="WMS 读取 PMS 商品主数据。",
        is_active=True,
    )

    class FakeDb:
        def get(self, model: object, key: object) -> object | None:
            rows = {
                (AppRegistryApp, "wms"): app_wms,
                (AppRegistryApp, "pms"): app_pms,
                (AppRegistryGatewayBinding, 1): gateway,
                (AppRegistryDependency, 1): dependency,
                (AppRegistryServiceClient, 1): client,
                (AppRegistryServicePermission, 1): permission,
            }
            return rows.get((model, key))

    service = SystemMonitoringCheckService(FakeDb())

    assert service.check_gateway_binding(1).status == "ok"
    assert service.check_dependency(1).status == "ok"
    assert service.check_service_client(1).status == "ok"
    assert service.check_service_permission(1).status == "ok"


def test_system_monitoring_check_service_updates_openapi_source_on_success() -> None:
    source = SimpleNamespace(
        id=6,
        app_code="erp",
        env_code="local",
        endpoint_id=30,
        openapi_url="http://127.0.0.1:7990/openapi.json",
        last_fetched_at=None,
        last_checksum=None,
        last_status="unknown",
        is_active=True,
        updated_at=None,
    )

    class FakeDb:
        committed = False
        rolled_back = False

        def get(self, model: object, key: object) -> object | None:
            if model is AppRegistryOpenApiSource and key == 6:
                return source
            return None

        def commit(self) -> None:
            self.committed = True

        def rollback(self) -> None:
            self.rolled_back = True

    fake_db = FakeDb()

    service = SystemMonitoringCheckService(
        fake_db,
        openapi_fetcher=lambda url, timeout: OpenApiFetchResult(
            http_status=200,
            raw_text='{"openapi":"3.1.0","paths":{}}',
            checksum="checksum-1",
            latency_ms=12,
        ),
    )

    result = service.check_openapi_source(6)

    assert result.status == "ok"
    assert source.last_status == "success"
    assert source.last_checksum == "checksum-1"
    assert source.last_fetched_at is not None
    assert fake_db.committed is True
    assert fake_db.rolled_back is False
