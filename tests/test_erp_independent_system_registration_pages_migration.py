from __future__ import annotations

from pathlib import Path

MIGRATION = Path("alembic/versions/0014_independent_system_registration_pages.py")


def test_route_prefixes_are_normalized_with_governance_fields() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "op.add_column" in text
    assert '"sort_order"' in text
    assert '"is_active"' in text
    assert "ix_page_route_prefixes_is_active" in text


def test_independent_system_registration_pages_are_declared() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "0014_independent_system_pages" in text
    assert "独立系统注册" in text

    expected = {
        "erp.system.apps.independent_systems": "/system/apps",
        "erp.system.apps.frontend_pages": "/system/apps/frontend-pages",
    }

    for code, route in expected.items():
        assert code in text
        assert route in text

    assert "独立系统列表" in text
    assert "独立系统前端页面目录" in text


def test_old_app_registry_metadata_tabs_are_deleted() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    retired_codes = {
        "erp.system.apps.basic",
        "erp.system.apps.components",
        "erp.system.apps.environments",
        "erp.system.apps.app_environments",
        "erp.system.apps.repositories",
        "erp.system.apps.gateway",
    }
    retired_routes = {
        "/system/apps/components",
        "/system/apps/environments",
        "/system/apps/app-environments",
        "/system/apps/repositories",
        "/system/apps/gateway",
    }

    for code in retired_codes:
        assert code in text

    for route in retired_routes:
        assert route in text

    assert "DELETE FROM page_route_prefixes" in text
    assert "DELETE FROM page_registry" in text


def test_independent_system_registration_pages_inherit_parent_permissions() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "'erp.system.apps'," in text
    assert "'erp'," in text
    assert "TRUE,\n                NULL,\n                NULL,\n                TRUE," in text
