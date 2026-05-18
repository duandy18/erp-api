from pathlib import Path

MIGRATION = Path("alembic/versions/0017_system_admin_child_pages.py")


def test_system_service_auth_child_pages_are_sidebar_pages() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "0017_system_child_pages" in text
    assert "0016_ind_sys_child_routes" in text
    assert "'erp.system.service_auth.capabilities'" in text
    assert "'erp.system.service_auth.permissions'" in text
    assert "'erp.system.service_auth.write_status'" in text
    assert "'/system/service-auth'" in text
    assert "'/system/service-auth/permissions'" in text
    assert "'/system/service-auth/write-status'" in text


def test_system_monitoring_child_pages_are_sidebar_pages() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    expected_pages = (
        "erp.system.monitoring.overview",
        "erp.system.monitoring.endpoints",
        "erp.system.monitoring.databases",
        "erp.system.monitoring.gateway",
        "erp.system.monitoring.dependencies",
        "erp.system.monitoring.service_auth",
        "erp.system.monitoring.openapi",
        "erp.system.monitoring.health",
    )

    for page_code in expected_pages:
        assert page_code in text

    assert "'/system/monitoring'" in text
    assert "'/system/monitoring/endpoints'" in text
    assert "'/system/monitoring/databases'" in text
    assert "'/system/monitoring/gateway'" in text
    assert "'/system/monitoring/dependencies'" in text
    assert "'/system/monitoring/service-auth'" in text
    assert "'/system/monitoring/openapi'" in text
    assert "'/system/monitoring/health'" in text


def test_system_parent_routes_are_removed_from_group_pages() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "DELETE FROM page_route_prefixes" in text
    assert "page_code = 'erp.system.service_auth'" in text
    assert "page_code = 'erp.system.monitoring'" in text
    assert "show_in_sidebar = TRUE" in text
