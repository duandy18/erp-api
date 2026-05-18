from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from app.main import app
from app.system_service_auth.contracts.system_service_auth_capability_contracts import (
    SystemServiceAuthCapabilityListOut,
)
from app.system_service_auth.services.system_service_auth_capability_service import (
    SystemServiceAuthCapabilityService,
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


class FakeRepo:
    def __init__(self) -> None:
        now = datetime.now(UTC)
        self.app = SimpleNamespace(code="wms", name="仓储管理", sort_order=10)
        self.capability = SimpleNamespace(
            app_code="wms",
            capability_code="wms.read.warehouses",
            capability_name="Read WMS warehouses",
            resource_code="warehouses",
            permission_code="wms.read.warehouses",
            description="read warehouses",
            is_active=True,
            source_updated_at=None,
            last_synced_at=now,
        )
        self.route = SimpleNamespace(
            app_code="wms",
            capability_code="wms.read.warehouses",
            http_method="GET",
            path="/wms/read/v1/warehouses",
            route_name="list_wms_read_warehouses",
            auth_required=True,
            is_active=True,
            source_created_at=None,
            last_synced_at=now,
        )

    def list_apps_by_codes(self, app_codes: set[str]):
        return [self.app] if "wms" in app_codes else []

    def list_capabilities(self, *, target_app_code: str | None = None):
        if target_app_code not in {None, "wms"}:
            return []
        return [self.capability]

    def list_routes(self, *, target_app_code: str | None = None):
        if target_app_code not in {None, "wms"}:
            return []
        return [self.route]


def test_system_service_auth_capabilities_route_is_mounted() -> None:
    assert ("GET", "/admin/system-service-auth/capabilities") in _method_paths()


def test_system_service_auth_capability_contract_shape() -> None:
    payload = SystemServiceAuthCapabilityListOut.model_validate(
        {
            "capabilities": [
                {
                    "target_app_code": "wms",
                    "target_app_name": "仓储管理",
                    "capability_code": "wms.read.warehouses",
                    "capability_name": "Read WMS warehouses",
                    "resource_code": "warehouses",
                    "permission_code": "wms.read.warehouses",
                    "description": "read warehouses",
                    "is_active": True,
                    "source_updated_at": None,
                    "last_synced_at": None,
                    "route_count": 0,
                    "routes": [],
                }
            ]
        }
    )

    assert payload.capabilities[0].target_app_code == "wms"
    assert payload.capabilities[0].route_count == 0


def test_system_service_auth_capability_service_groups_routes() -> None:
    service = SystemServiceAuthCapabilityService(
        SimpleNamespace(),
        repository=FakeRepo(),  # type: ignore[arg-type]
    )

    payload = service.list_capabilities(target_app_code="wms")

    assert len(payload.capabilities) == 1
    capability = payload.capabilities[0]
    assert capability.target_app_code == "wms"
    assert capability.target_app_name == "仓储管理"
    assert capability.capability_code == "wms.read.warehouses"
    assert capability.route_count == 1
    assert capability.routes[0].path == "/wms/read/v1/warehouses"
