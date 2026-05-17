from __future__ import annotations

from pathlib import Path

from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryServiceClient,
    AppRegistryServicePermission,
)
from app.db.base import Base


def test_app_registry_service_auth_models_are_registered() -> None:
    assert AppRegistryServiceClient.__table__.name == "app_registry_service_clients"
    assert AppRegistryServicePermission.__table__.name == "app_registry_service_permissions"
    assert "app_registry_service_clients" in set(Base.metadata.tables)
    assert "app_registry_service_permissions" in set(Base.metadata.tables)


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
