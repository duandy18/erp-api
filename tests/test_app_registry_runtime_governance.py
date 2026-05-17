from __future__ import annotations

from pathlib import Path

from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryHealthCheck,
    AppRegistryHealthCheckRun,
    AppRegistryOpenApiSource,
)
from app.db.base import Base


def test_app_registry_runtime_governance_models_are_registered() -> None:
    assert AppRegistryHealthCheck.__table__.name == "app_registry_health_checks"
    assert AppRegistryHealthCheckRun.__table__.name == "app_registry_health_check_runs"
    assert AppRegistryOpenApiSource.__table__.name == "app_registry_openapi_sources"

    assert "app_registry_health_checks" in set(Base.metadata.tables)
    assert "app_registry_health_check_runs" in set(Base.metadata.tables)
    assert "app_registry_openapi_sources" in set(Base.metadata.tables)


def test_app_registry_runtime_governance_migration_contains_tables_and_seed() -> None:
    migration = Path("alembic/versions/0009_app_registry_runtime_governance.py").read_text()

    assert "app_registry_health_checks" in migration
    assert "app_registry_health_check_runs" in migration
    assert "app_registry_openapi_sources" in migration
    assert "endpoint_type IN ('health', 'db_health')" in migration
    assert "endpoint_type = 'openapi'" in migration
    assert "DATABASE_URL" not in migration
