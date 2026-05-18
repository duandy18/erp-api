from __future__ import annotations

from pathlib import Path

from app.app_registry.models.app_registry_iam_projection import (
    AppRegistryIamPageProjection,
    AppRegistryIamPageRoutePrefixProjection,
    AppRegistryIamPermissionProjection,
    AppRegistryIamSyncRun,
    AppRegistryIamUserPermissionProjection,
    AppRegistryIamUserProjection,
)
from app.db.base import Base

MIGRATION = Path("alembic/versions/0020_app_registry_iam_projection.py")


def test_system_iam_projection_models_are_registered() -> None:
    expected = {
        "app_registry_iam_sync_runs",
        "app_registry_iam_user_projection",
        "app_registry_iam_permission_projection",
        "app_registry_iam_user_permission_projection",
        "app_registry_iam_page_projection",
        "app_registry_iam_page_route_prefix_projection",
    }

    assert AppRegistryIamSyncRun.__tablename__ in expected
    assert AppRegistryIamUserProjection.__tablename__ in expected
    assert AppRegistryIamPermissionProjection.__tablename__ in expected
    assert AppRegistryIamUserPermissionProjection.__tablename__ in expected
    assert AppRegistryIamPageProjection.__tablename__ in expected
    assert AppRegistryIamPageRoutePrefixProjection.__tablename__ in expected

    assert expected.issubset(set(Base.metadata.tables))


def test_system_iam_projection_unique_keys_are_app_scoped() -> None:
    user_constraints = {c.name for c in AppRegistryIamUserProjection.__table__.constraints}
    permission_constraints = {
        c.name for c in AppRegistryIamPermissionProjection.__table__.constraints
    }
    user_permission_constraints = {
        c.name for c in AppRegistryIamUserPermissionProjection.__table__.constraints
    }
    page_constraints = {c.name for c in AppRegistryIamPageProjection.__table__.constraints}
    route_constraints = {
        c.name for c in AppRegistryIamPageRoutePrefixProjection.__table__.constraints
    }

    assert "uq_app_reg_iam_user_app_source_user" in user_constraints
    assert "uq_app_reg_iam_perm_app_code" in permission_constraints
    assert "uq_app_reg_iam_user_perm_identity" in user_permission_constraints
    assert "uq_app_reg_iam_page_app_page" in page_constraints
    assert "uq_app_reg_iam_route_prefix_identity" in route_constraints


def test_system_iam_projection_migration_contains_expected_tables() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    for table_name in {
        "app_registry_iam_sync_runs",
        "app_registry_iam_user_projection",
        "app_registry_iam_permission_projection",
        "app_registry_iam_user_permission_projection",
        "app_registry_iam_page_projection",
        "app_registry_iam_page_route_prefix_projection",
    }:
        assert table_name in text

    assert "app_registry_apps.code" in text
    assert "source_user_id" in text
    assert "source_permission_id" in text
    assert "system/read/v1/iam-snapshot" not in text
    assert "http://127.0.0.1" not in text
