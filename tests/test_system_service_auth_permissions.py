from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from app.main import app
from app.system_service_auth.contracts.system_service_auth_permission_contracts import (
    SystemServiceAuthPermissionCreateIn,
    SystemServiceAuthPermissionListOut,
    SystemServiceAuthPermissionUpdateIn,
)
from app.system_service_auth.services.system_service_auth_permission_service import (
    SystemServiceAuthPermissionService,
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
        self.apps = [
            SimpleNamespace(code="wms", name="WMS 仓储执行系统", sort_order=10),
            SimpleNamespace(code="pms", name="PMS 商品主数据系统", sort_order=20),
        ]
        self.client = SimpleNamespace(
            id=1,
            app_code="wms",
            client_code="wms-service",
            client_name="WMS Service Client",
            auth_type="none",
            secret_ref=None,
            is_active=True,
        )
        self.capability = SimpleNamespace(
            app_code="pms",
            capability_code="pms.read.items",
            capability_name="Read PMS items",
            permission_code="pms.read.items",
            description="读取 PMS 商品主数据",
            is_active=True,
            last_synced_at=now,
        )
        self.permission = SimpleNamespace(
            id=1,
            client_id=1,
            source_app_code="wms",
            target_app_code="pms",
            permission_code="pms.read.items",
            description="WMS 读取 PMS 商品主数据",
            is_active=False,
            created_at=now,
            updated_at=now,
        )

    def list_apps(self) -> list[object]:
        return self.apps

    def list_clients(self) -> list[object]:
        return [self.client]

    def get_client(self, client_id: int) -> object | None:
        return self.client if client_id == 1 else None

    def list_capability_options(self) -> list[object]:
        return [self.capability]

    def get_capability_by_permission(
        self,
        *,
        target_app_code: str,
        permission_code: str,
    ) -> object | None:
        if target_app_code == "pms" and permission_code == "pms.read.items":
            return self.capability
        return None

    def list_permissions(self) -> list[object]:
        return [self.permission]

    def get_permission(self, permission_id: int) -> object | None:
        return self.permission if permission_id == 1 else None

    def find_permission(self, *, client_id: int, permission_code: str) -> object | None:
        return None

    def save_permission(self, row: object) -> object:
        if getattr(row, "id", None) is None:
            row.id = 9
        if getattr(row, "created_at", None) is None:
            row.created_at = datetime.now(UTC)
        if getattr(row, "updated_at", None) is None:
            row.updated_at = datetime.now(UTC)
        return row


def test_system_service_auth_permission_routes_are_mounted() -> None:
    pairs = _method_paths()

    assert ("GET", "/admin/system-service-auth/permissions") in pairs
    assert ("POST", "/admin/system-service-auth/permissions") in pairs
    assert ("PATCH", "/admin/system-service-auth/permissions/{permission_id}") in pairs


def test_system_service_auth_permission_contract_shape() -> None:
    payload = SystemServiceAuthPermissionListOut.model_validate(
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
                    "is_active": True,
                }
            ],
            "capability_options": [
                {
                    "target_app_code": "pms",
                    "target_app_name": "PMS 商品主数据系统",
                    "capability_code": "pms.read.items",
                    "capability_name": "Read PMS items",
                    "permission_code": "pms.read.items",
                    "description": "读取 PMS 商品主数据",
                    "is_active": True,
                    "last_synced_at": None,
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
                    "description": "WMS 读取 PMS 商品主数据",
                    "is_active": False,
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC),
                    "capability_code": "pms.read.items",
                    "capability_name": "Read PMS items",
                    "capability_active": True,
                }
            ],
        }
    )

    assert payload.clients[0].client_code == "wms-service"
    assert payload.capability_options[0].permission_code == "pms.read.items"
    assert payload.permissions[0].permission_code == "pms.read.items"


def test_system_service_auth_permission_service_lists_context() -> None:
    service = SystemServiceAuthPermissionService(
        SimpleNamespace(),
        repository=FakeRepo(),  # type: ignore[arg-type]
    )

    payload = service.list_permissions()

    assert payload.clients[0].app_name == "WMS 仓储执行系统"
    assert payload.capability_options[0].target_app_code == "pms"
    assert payload.permissions[0].client_code == "wms-service"
    assert payload.permissions[0].capability_code == "pms.read.items"


def test_system_service_auth_permission_service_creates_permission() -> None:
    service = SystemServiceAuthPermissionService(
        SimpleNamespace(),
        repository=FakeRepo(),  # type: ignore[arg-type]
    )

    payload = service.create_permission(
        SystemServiceAuthPermissionCreateIn(
            client_id=1,
            target_app_code="pms",
            permission_code="pms.read.items",
            description="WMS 读取 PMS 商品主数据",
            is_active=True,
        )
    )

    assert payload.permission_id == 9
    assert payload.source_app_code == "wms"
    assert payload.target_app_code == "pms"
    assert payload.permission_code == "pms.read.items"
    assert payload.is_active is True


def test_system_service_auth_permission_service_updates_permission() -> None:
    service = SystemServiceAuthPermissionService(
        SimpleNamespace(),
        repository=FakeRepo(),  # type: ignore[arg-type]
    )

    payload = service.update_permission(
        1,
        SystemServiceAuthPermissionUpdateIn(
            description="更新说明",
            is_active=True,
        ),
    )

    assert payload.description == "更新说明"
    assert payload.is_active is True
