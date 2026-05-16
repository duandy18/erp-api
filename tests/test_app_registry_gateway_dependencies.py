from __future__ import annotations

from pathlib import Path

from app.app_registry.contracts.app_registry_app_metadata_contracts import (
    AppRegistryAppMetadataOut,
)
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryDependency,
    AppRegistryGatewayBinding,
)
from app.db.base import Base


def test_app_registry_gateway_and_dependency_models_are_registered() -> None:
    assert AppRegistryGatewayBinding.__table__.name == "app_registry_gateway_bindings"
    assert AppRegistryDependency.__table__.name == "app_registry_dependencies"
    assert "app_registry_gateway_bindings" in set(Base.metadata.tables)
    assert "app_registry_dependencies" in set(Base.metadata.tables)


def test_app_registry_profile_contract_includes_gateway_and_dependencies() -> None:
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
            "components": [],
            "environments": [],
            "app_environments": [],
            "endpoints": [],
            "databases": [],
            "repositories": [],
            "gateway_bindings": [
                {
                    "id": 1,
                    "app_code": "wms",
                    "env_code": "local",
                    "web_path": "/wms",
                    "api_path": "/api/wms",
                    "web_upstream_url": "http://host.docker.internal:5173",
                    "api_upstream_url": "http://host.docker.internal:8000",
                    "rewrite_mode": "preserve_prefix",
                    "is_published": False,
                    "published_at": None,
                    "is_active": True,
                }
            ],
            "outgoing_dependencies": [
                {
                    "id": 1,
                    "source_app_code": "wms",
                    "target_app_code": "pms",
                    "dependency_type": "projection_feed",
                    "description": "WMS 读取 PMS 商品主数据投影和校验合同。",
                    "is_required": True,
                    "status": "ready",
                    "is_active": True,
                }
            ],
            "incoming_dependencies": [],
        }
    )

    assert payload.gateway_bindings[0].is_published is False
    assert payload.outgoing_dependencies[0].target_app_code == "pms"


def test_app_registry_links_migration_contains_gateway_and_dependencies() -> None:
    migration = Path("alembic/versions/0007_app_registry_links.py").read_text()

    assert "app_registry_gateway_bindings" in migration
    assert "app_registry_dependencies" in migration
    assert "'erp'" in migration
    assert "'/api/erp'" in migration
    assert "'wms'" in migration
    assert "'pms'" in migration
    assert "host.docker.internal:7990" in migration
