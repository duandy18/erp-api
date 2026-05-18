from pathlib import Path

MIGRATION = Path("alembic/versions/0016_independent_system_child_routes.py")


def test_independent_system_children_own_sidebar_routes() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "0016_ind_sys_child_routes" in text
    assert "0015_ind_sys_parent_route" in text
    assert "'erp.system.apps.independent_systems'" in text
    assert "'erp.system.apps.frontend_pages'" in text
    assert "'/system/apps'" in text
    assert "'/system/apps/frontend-pages'" in text


def test_independent_system_parent_no_longer_owns_apps_route() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "DELETE FROM page_route_prefixes" in text
    assert "page_code = 'erp.system.apps'" in text
    assert "route_prefix = '/system/apps'" in text
    assert "show_in_sidebar = TRUE" in text
