from __future__ import annotations

from pathlib import Path

from app.app_registry.contracts.app_registry_app_metadata_contracts import (
    AppRegistryAppMetadataListOut,
    AppRegistryAppMetadataOut,
)
from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryComponent,
    AppRegistryDatabase,
    AppRegistryEndpoint,
    AppRegistryEnvironment,
    AppRegistryRepositoryMeta,
)
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


def test_app_registry_app_metadata_routes_are_mounted() -> None:
    pairs = _method_paths()

    assert ("GET", "/admin/app-registry/app-metadata") in pairs
    assert ("GET", "/admin/app-registry/app-metadata/{app_code}") in pairs


def test_app_registry_app_metadata_models_are_registered() -> None:
    expected_tables = {
        "app_registry_components",
        "app_registry_environments",
        "app_registry_app_environments",
        "app_registry_endpoints",
        "app_registry_databases",
        "app_registry_repositories",
    }

    assert "domain_code" in AppRegistryApp.__table__.c
    assert "app_type" in AppRegistryApp.__table__.c
    assert AppRegistryComponent.__table__.name == "app_registry_components"
    assert AppRegistryEnvironment.__table__.name == "app_registry_environments"
    assert AppRegistryEndpoint.__table__.name == "app_registry_endpoints"
    assert AppRegistryDatabase.__table__.name == "app_registry_databases"
    assert AppRegistryRepositoryMeta.__table__.name == "app_registry_repositories"
    assert expected_tables.issubset(set(Base.metadata.tables))


def test_app_registry_app_metadata_contract_shape() -> None:
    profile = AppRegistryAppMetadataOut.model_validate(
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
        }
    )

    assert profile.app.code == "wms"
    assert profile.app.domain_code == "wms"


def test_app_registry_app_metadatas_contract_shape() -> None:
    payload = AppRegistryAppMetadataListOut.model_validate({"profiles": []})

    assert payload.profiles == []


def test_app_registry_app_metadata_migration_contains_foundation_tables() -> None:
    migration = Path(
        "alembic/versions/0006_app_registry_profile.py"
    ).read_text()

    assert "app_registry_components" in migration
    assert "app_registry_environments" in migration
    assert "app_registry_endpoints" in migration
    assert "app_registry_databases" in migration
    assert "app_registry_repositories" in migration
    assert "ERP_DATABASE_URL" in migration
    assert "WMS_DATABASE_URL" in migration
    assert "postgresql://" not in migration
