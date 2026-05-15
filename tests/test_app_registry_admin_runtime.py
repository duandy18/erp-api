from __future__ import annotations

from pathlib import Path

from app.app_registry.contracts.app_registry_admin_contracts import (
    AppRegistryAdminAppCreateIn,
    AppRegistryAdminAppsOut,
    AppRegistryAdminAppUpdateIn,
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


def test_admin_app_registry_routes_are_mounted() -> None:
    pairs = _method_paths()

    assert ("GET", "/admin/app-registry/apps") in pairs
    assert ("POST", "/admin/app-registry/apps") in pairs
    assert ("PATCH", "/admin/app-registry/apps/{code}") in pairs
    assert ("POST", "/admin/app-registry/apps/{code}/enable") in pairs
    assert ("POST", "/admin/app-registry/apps/{code}/disable") in pairs


def test_admin_app_registry_create_contract_shape() -> None:
    body = AppRegistryAdminAppCreateIn.model_validate(
        {
            "code": "billing",
            "name": "Billing 财务系统",
            "description": "财务结算、对账与账单控制面入口。",
            "web_path": "/billing",
            "api_path": "/api/billing",
            "local_web_url": "http://127.0.0.1:5178",
            "local_api_url": "http://127.0.0.1:8025",
            "status": "planned",
            "sort_order": 60,
            "is_active": False,
        }
    )

    assert body.code == "billing"
    assert body.status == "planned"
    assert body.is_active is False


def test_admin_app_registry_update_contract_shape() -> None:
    body = AppRegistryAdminAppUpdateIn.model_validate(
        {
            "name": "Billing 财务系统",
            "status": "ready",
            "sort_order": 65,
            "is_active": True,
        }
    )

    assert body.name == "Billing 财务系统"
    assert body.status == "ready"
    assert body.sort_order == 65
    assert body.is_active is True


def test_admin_app_registry_list_contract_shape() -> None:
    payload = AppRegistryAdminAppsOut.model_validate(
        {
            "apps": [
                {
                    "code": "wms",
                    "name": "WMS 仓储执行系统",
                    "description": "库存、入库、出库、仓内执行。",
                    "web_path": "/wms",
                    "api_path": "/api/wms",
                    "local_web_url": "http://127.0.0.1:5173",
                    "local_api_url": "http://127.0.0.1:8000",
                    "status": "ready",
                    "sort_order": 10,
                    "is_active": True,
                }
            ]
        }
    )

    assert payload.apps[0].code == "wms"
    assert payload.apps[0].is_active is True


def test_app_registry_admin_page_migration_registers_system_apps_page() -> None:
    migration = Path("alembic/versions/0005_erp_app_registry_admin_page.py").read_text()

    assert "erp.system.apps" in migration
    assert "/system/apps" in migration
