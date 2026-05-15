from __future__ import annotations

from pathlib import Path

from app.app_registry.contracts.app_registry_system_profile_contracts import (
    AppRegistrySystemProfileOut,
)
from app.app_registry.models.app_registry_system_metadata import (
    AppRegistryServiceClient,
    AppRegistryServicePermission,
)
from app.db.base import Base


def test_app_registry_service_auth_models_are_registered() -> None:
    assert AppRegistryServiceClient.__table__.name == "app_registry_service_clients"
    assert AppRegistryServicePermission.__table__.name == "app_registry_service_permissions"
    assert "app_registry_service_clients" in set(Base.metadata.tables)
    assert "app_registry_service_permissions" in set(Base.metadata.tables)


def test_app_registry_profile_contract_includes_service_auth() -> None:
    payload = AppRegistrySystemProfileOut.model_validate(
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
            "components": [],
            "environments": [],
            "app_environments": [],
            "endpoints": [],
            "databases": [],
            "repositories": [],
            "gateway_bindings": [],
            "outgoing_dependencies": [],
            "incoming_dependencies": [],
            "service_clients": [
                {
                    "id": 1,
                    "app_code": "wms",
                    "client_code": "wms-service",
                    "client_name": "WMS Service Client",
                    "auth_type": "none",
                    "secret_ref": None,
                    "is_active": False,
                }
            ],
            "service_permissions": [
                {
                    "id": 1,
                    "client_id": 1,
                    "client_code": "wms-service",
                    "client_name": "WMS Service Client",
                    "source_app_code": "wms",
                    "target_app_code": "pms",
                    "permission_code": "pms.read.items",
                    "description": "WMS 读取 PMS 商品主数据。",
                    "is_active": False,
                }
            ],
        }
    )

    assert payload.service_clients[0].client_code == "wms-service"
    assert payload.service_clients[0].is_active is False
    assert payload.service_permissions[0].client_code == "wms-service"
    assert payload.service_permissions[0].client_name == "WMS Service Client"
    assert payload.service_permissions[0].permission_code == "pms.read.items"


def test_app_registry_service_auth_migration_contains_seed() -> None:
    migration = Path("alembic/versions/0008_app_registry_auth.py").read_text()

    assert "app_registry_service_clients" in migration
    assert "app_registry_service_permissions" in migration
    assert "wms-service" in migration
    assert "oms-service" in migration
    assert "procurement-service" in migration
    assert "logistics-service" in migration
    assert "pms.read.items" in migration
    assert "wms.write.inbound" in migration
    assert "wms.read.shipping_handoffs" in migration
    assert "DATABASE_URL" not in migration
