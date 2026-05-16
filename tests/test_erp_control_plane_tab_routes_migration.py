from pathlib import Path

MIGRATION = Path("alembic/versions/0011_erp_control_plane_tab_routes.py")


def test_control_plane_tab_routes_are_registered_as_hidden_pages() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "0011_erp_tabs" in text
    assert "0010_erp_pages" in text
    assert "show_in_sidebar" in text
    assert "FALSE,\n            TRUE,\n            NULL,\n            NULL" in text


def test_app_registration_tab_routes_are_registered() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    expected = {
        "erp.system.apps.basic": "/system/apps",
        "erp.system.apps.components": "/system/apps/components",
        "erp.system.apps.environments": "/system/apps/environments",
        "erp.system.apps.app_environments": "/system/apps/app-environments",
        "erp.system.apps.repositories": "/system/apps/repositories",
        "erp.system.apps.gateway": "/system/apps/gateway",
    }

    for code, route in expected.items():
        assert code in text
        assert route in text


def test_monitoring_tab_routes_are_registered() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    expected = {
        "erp.system.monitoring.overview": "/system/monitoring",
        "erp.system.monitoring.endpoints": "/system/monitoring/endpoints",
        "erp.system.monitoring.databases": "/system/monitoring/databases",
        "erp.system.monitoring.gateway": "/system/monitoring/gateway",
        "erp.system.monitoring.dependencies": "/system/monitoring/dependencies",
        "erp.system.monitoring.service_auth": "/system/monitoring/service-auth",
        "erp.system.monitoring.openapi": "/system/monitoring/openapi",
        "erp.system.monitoring.health": "/system/monitoring/health",
    }

    for code, route in expected.items():
        assert code in text
        assert route in text


def test_service_auth_tab_routes_are_registered() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    expected = {
        "erp.system.service_auth.capabilities": "/system/service-auth/capabilities",
        "erp.system.service_auth.permissions": "/system/service-auth/permissions",
        "erp.system.service_auth.write_status": "/system/service-auth/write-status",
    }

    for code, route in expected.items():
        assert code in text
        assert route in text
