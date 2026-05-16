from pathlib import Path

MIGRATION = Path("alembic/versions/0010_erp_control_plane_page_registry.py")


def test_control_plane_page_registry_migration_registers_final_pages() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "erp.apps" in text
    assert "我的应用" in text
    assert "erp.system.users" in text
    assert "用户与权限" in text
    assert "erp.system.apps" in text
    assert "应用注册" in text
    assert "erp.system.service_auth" in text
    assert "系统协作配置" in text
    assert "erp.system.monitoring" in text
    assert "系统监控" in text


def test_control_plane_page_registry_migration_retires_redundant_pages() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "erp.portal" in text
    assert "erp.cockpit" in text
    assert "page.erp.portal.read" in text
    assert "page.erp.cockpit.read" in text
    assert "erp.system.audit" in text


def test_control_plane_page_registry_migration_keeps_system_children_inherited() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "'erp.system.service_auth'," in text
    assert "'erp.system.monitoring'," in text
    assert "'erp.system'," in text
    assert "TRUE,\n            NULL,\n            NULL,\n            30" in text
    assert "TRUE,\n            NULL,\n            NULL,\n            40" in text
