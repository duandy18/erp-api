from __future__ import annotations

from pathlib import Path

from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryDatabase,
    AppRegistryEndpoint,
    AppRegistryGatewayBinding,
    AppRegistryHealthCheck,
    AppRegistryOpenApiSource,
)
from app.db.base import Base


def test_retired_app_registry_metadata_tables_are_not_registered() -> None:
    retired_tables = {
        "app_registry_components",
        "app_registry_environments",
        "app_registry_app_environments",
        "app_registry_repositories",
    }

    for table_name in retired_tables:
        assert table_name not in Base.metadata.tables


def test_app_registry_runtime_tables_keep_env_code_without_environment_fk() -> None:
    assert "component_id" not in AppRegistryEndpoint.__table__.c

    runtime_tables = [
        AppRegistryEndpoint.__table__,
        AppRegistryDatabase.__table__,
        AppRegistryGatewayBinding.__table__,
        AppRegistryHealthCheck.__table__,
        AppRegistryOpenApiSource.__table__,
    ]

    for table in runtime_tables:
        assert "env_code" in table.c
        assert table.c.env_code.foreign_keys == set()


def test_app_registry_metadata_retirement_migration_contract() -> None:
    migration = Path(
        "alembic/versions/0012_app_registry_metadata_retirement.py"
    ).read_text()

    assert 'op.drop_table("app_registry_repositories")' in migration
    assert 'op.drop_table("app_registry_app_environments")' in migration
    assert 'op.drop_table("app_registry_components")' in migration
    assert 'op.drop_table("app_registry_environments")' in migration
    assert 'op.drop_column("app_registry_endpoints", "component_id")' in migration

    assert "fk_app_registry_endpoints_component_id_components" in migration
    assert "fk_app_registry_endpoints_env_code_environments" in migration
    assert "fk_app_registry_databases_env_code_environments" in migration
    assert "fk_app_registry_gateway_bindings_env_code_environments" in migration
    assert "fk_app_registry_health_checks_env_code_environments" in migration
    assert "fk_app_registry_openapi_sources_env_code_environments" in migration
