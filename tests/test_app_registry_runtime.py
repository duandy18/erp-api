from __future__ import annotations

from app.app_registry.contracts.app_registry_contracts import AppRegistryAppsOut
from app.app_registry.models.app_registry_app import AppRegistryApp
from app.db.base import Base
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


def test_app_registry_route_is_mounted() -> None:
    assert ("GET", "/erp/app-registry/apps") in _method_paths()


def test_app_registry_model_is_registered_in_metadata() -> None:
    assert AppRegistryApp.__table__.name == "app_registry_apps"
    assert "app_registry_apps" in set(Base.metadata.tables)


def test_app_registry_contract_shape() -> None:
    payload = AppRegistryAppsOut.model_validate(
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
    assert payload.apps[0].web_path == "/wms"
