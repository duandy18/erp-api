from pathlib import Path

MIGRATION = Path("alembic/versions/0019_user_permission_child_pages.py")


def test_user_permission_child_pages_are_registered() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "0019_user_permission_pages" in text
    assert "0018_service_auth_write_status" in text

    assert "'erp.system.users'" in text
    assert "'用户与权限'" in text

    assert "erp.system.users.independent_system_user_permissions" in text
    assert "独立系统用户权限表" in text
    assert "/system/users" in text

    assert "erp.system.users.permission_config" in text
    assert "用户权限配置表" in text
    assert "/system/users/permission-config" in text


def test_user_permission_parent_no_longer_owns_business_route() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "DELETE FROM page_route_prefixes" in text
    assert "page_code = 'erp.system.users'" in text
    assert "真实业务路由交给子页面" in text

    assert "level = 2" in text
    assert "show_in_sidebar = TRUE" in text


def test_user_permission_child_pages_inherit_parent_permissions() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "'erp.system.users'," in text
    assert "3," in text
    assert "'erp'," in text
    assert "TRUE,\n              NULL,\n              NULL" in text


def test_user_permission_child_page_routes_do_not_require_route_prefix_unique_index() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "ON CONFLICT (route_prefix)" not in text
    assert "DELETE FROM page_route_prefixes" in text
