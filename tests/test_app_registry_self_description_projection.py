from __future__ import annotations

from pathlib import Path

from app.app_registry.models.app_registry_self_description_projection import (
    AppRegistryAppManifestSnapshot,
    AppRegistryPageCatalogPage,
    AppRegistrySelfDescriptionSyncRun,
    AppRegistryServiceCapabilityCatalog,
    AppRegistryServiceCapabilityRoute,
    AppRegistryServiceDependencyCatalog,
    AppRegistryServiceDependencyEndpoint,
)
from app.db.base import Base

MIGRATION = Path("alembic/versions/0013_app_registry_self_description_projections.py")


def test_self_description_projection_models_are_registered() -> None:
    expected = {
        "app_registry_self_description_sync_runs",
        "app_registry_app_manifest_snapshots",
        "app_registry_page_catalog_pages",
        "app_registry_service_capability_catalog",
        "app_registry_service_capability_routes",
        "app_registry_service_dependency_catalog",
        "app_registry_service_dependency_endpoints",
    }

    assert AppRegistrySelfDescriptionSyncRun.__tablename__ in expected
    assert AppRegistryAppManifestSnapshot.__tablename__ in expected
    assert AppRegistryPageCatalogPage.__tablename__ in expected
    assert AppRegistryServiceCapabilityCatalog.__tablename__ in expected
    assert AppRegistryServiceCapabilityRoute.__tablename__ in expected
    assert AppRegistryServiceDependencyCatalog.__tablename__ in expected
    assert AppRegistryServiceDependencyEndpoint.__tablename__ in expected

    assert expected.issubset(set(Base.metadata.tables))


def test_self_description_projection_model_keys_are_composite_where_needed() -> None:
    page_table = AppRegistryPageCatalogPage.__table__
    capability_table = AppRegistryServiceCapabilityCatalog.__table__
    dependency_table = AppRegistryServiceDependencyCatalog.__table__

    page_unique_names = {constraint.name for constraint in page_table.constraints}
    capability_unique_names = {constraint.name for constraint in capability_table.constraints}
    dependency_unique_names = {constraint.name for constraint in dependency_table.constraints}

    assert "uq_app_registry_page_catalog_pages_app_page" in page_unique_names
    assert (
        "uq_app_registry_service_capability_catalog_app_capability"
        in capability_unique_names
    )
    assert (
        "uq_app_registry_service_dependency_catalog_source_dependency"
        in dependency_unique_names
    )


def test_self_description_projection_migration_contains_expected_tables() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    expected_tables = {
        "app_registry_self_description_sync_runs",
        "app_registry_app_manifest_snapshots",
        "app_registry_page_catalog_pages",
        "app_registry_service_capability_catalog",
        "app_registry_service_capability_routes",
        "app_registry_service_dependency_catalog",
        "app_registry_service_dependency_endpoints",
    }

    for table_name in expected_tables:
        assert table_name in text

    assert "system/read/v1" not in text
    assert "DATABASE_URL" not in text
    assert "app_registry_service_permissions" not in text
