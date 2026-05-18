from pathlib import Path

MIGRATION = Path("alembic/versions/0015_independent_system_registration_parent_route.py")


def test_independent_system_parent_page_owns_sidebar_route() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "'erp.system.apps'" in text
    assert "'/system/apps'" in text
    assert "DELETE FROM page_route_prefixes" in text
    assert "route_prefix = '/system/apps'" in text
    assert "page_code <> 'erp.system.apps'" in text


def test_independent_system_children_do_not_add_sidebar_entries() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "'erp.system.apps.independent_systems'" in text
    assert "'erp.system.apps.frontend_pages'" in text
    assert "show_in_sidebar = FALSE" in text
    assert "'/system/apps/frontend-pages'" in text
