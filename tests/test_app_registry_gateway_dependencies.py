from __future__ import annotations

from pathlib import Path

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


def test_app_registry_links_migration_contains_gateway_and_dependencies() -> None:
    migration = Path("alembic/versions/0007_app_registry_links.py").read_text()

    assert "app_registry_gateway_bindings" in migration
    assert "app_registry_dependencies" in migration
    assert "'erp'" in migration
    assert "'/api/erp'" in migration
    assert "'wms'" in migration
    assert "'pms'" in migration
    assert "host.docker.internal:7990" in migration
