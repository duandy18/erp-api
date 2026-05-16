"""erp_control_plane_tab_routes

Revision ID: 0011_erp_tabs
Revises: 0010_erp_pages
Create Date: 2026-05-16 22:30:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0011_erp_tabs"
down_revision: str | Sequence[str] | None = "0010_erp_pages"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


APP_REGISTRATION_TAB_PAGES = (
    (
        "erp.system.apps.basic",
        "基础信息",
        "/system/apps",
        10,
    ),
    (
        "erp.system.apps.components",
        "组件",
        "/system/apps/components",
        20,
    ),
    (
        "erp.system.apps.environments",
        "环境",
        "/system/apps/environments",
        30,
    ),
    (
        "erp.system.apps.app_environments",
        "应用环境",
        "/system/apps/app-environments",
        40,
    ),
    (
        "erp.system.apps.repositories",
        "仓库",
        "/system/apps/repositories",
        50,
    ),
    (
        "erp.system.apps.gateway",
        "Gateway 配置",
        "/system/apps/gateway",
        60,
    ),
)

MONITORING_TAB_PAGES = (
    (
        "erp.system.monitoring.overview",
        "应用运行总览",
        "/system/monitoring",
        10,
    ),
    (
        "erp.system.monitoring.endpoints",
        "API 状态",
        "/system/monitoring/endpoints",
        20,
    ),
    (
        "erp.system.monitoring.databases",
        "数据库状态",
        "/system/monitoring/databases",
        30,
    ),
    (
        "erp.system.monitoring.gateway",
        "Gateway 状态",
        "/system/monitoring/gateway",
        40,
    ),
    (
        "erp.system.monitoring.dependencies",
        "系统依赖状态",
        "/system/monitoring/dependencies",
        50,
    ),
    (
        "erp.system.monitoring.service_auth",
        "Service Auth 状态",
        "/system/monitoring/service-auth",
        60,
    ),
    (
        "erp.system.monitoring.openapi",
        "OpenAPI 合同状态",
        "/system/monitoring/openapi",
        70,
    ),
    (
        "erp.system.monitoring.health",
        "健康检查",
        "/system/monitoring/health",
        80,
    ),
)

SERVICE_AUTH_TAB_PAGES = (
    (
        "erp.system.service_auth.capabilities",
        "能力目录",
        "/system/service-auth/capabilities",
        10,
    ),
    (
        "erp.system.service_auth.permissions",
        "调用授权",
        "/system/service-auth/permissions",
        20,
    ),
    (
        "erp.system.service_auth.write_status",
        "写入状态",
        "/system/service-auth/write-status",
        30,
    ),
)


def _insert_tab_pages(parent_code: str, rows: tuple[tuple[str, str, str, int], ...]) -> None:
    values_sql = ",\n".join(
        f"""(
            '{code}',
            '{name}',
            '{parent_code}',
            3,
            'erp',
            FALSE,
            FALSE,
            TRUE,
            NULL,
            NULL,
            {sort_order},
            TRUE
          )"""
        for code, name, _route_prefix, sort_order in rows
    )

    op.execute(
        f"""
        INSERT INTO page_registry (
          code,
          name,
          parent_code,
          level,
          domain_code,
          show_in_topbar,
          show_in_sidebar,
          inherit_permissions,
          read_permission_id,
          write_permission_id,
          sort_order,
          is_active
        )
        VALUES
          {values_sql}
        ON CONFLICT (code) DO UPDATE
        SET
          name = EXCLUDED.name,
          parent_code = EXCLUDED.parent_code,
          level = EXCLUDED.level,
          domain_code = EXCLUDED.domain_code,
          show_in_topbar = EXCLUDED.show_in_topbar,
          show_in_sidebar = EXCLUDED.show_in_sidebar,
          inherit_permissions = EXCLUDED.inherit_permissions,
          read_permission_id = EXCLUDED.read_permission_id,
          write_permission_id = EXCLUDED.write_permission_id,
          sort_order = EXCLUDED.sort_order,
          is_active = EXCLUDED.is_active,
          updated_at = now()
        """
    )


def _insert_route_prefixes(rows: tuple[tuple[str, str, str, int], ...]) -> None:
    values_sql = ",\n".join(
        f"('{code}', '{route_prefix}')"
        for code, _name, route_prefix, _sort_order in rows
    )

    op.execute(
        f"""
        INSERT INTO page_route_prefixes (page_code, route_prefix)
        VALUES
          {values_sql}
        ON CONFLICT (page_code, route_prefix) DO NOTHING
        """
    )


def upgrade() -> None:
    """Register control-plane tab routes as hidden page entries.

    这些页面不进入左侧菜单，但进入 page_registry，用于：
    - 保留 tab 的独立路由。
    - 让用户导航 route_prefixes 能识别 tab 路由归属。
    - 继承所属二级页面权限，不新增权限矩阵列。
    """

    _insert_tab_pages("erp.system.apps", APP_REGISTRATION_TAB_PAGES)
    _insert_tab_pages("erp.system.monitoring", MONITORING_TAB_PAGES)
    _insert_tab_pages("erp.system.service_auth", SERVICE_AUTH_TAB_PAGES)

    _insert_route_prefixes(APP_REGISTRATION_TAB_PAGES)
    _insert_route_prefixes(MONITORING_TAB_PAGES)
    _insert_route_prefixes(SERVICE_AUTH_TAB_PAGES)


def downgrade() -> None:
    """Remove hidden control-plane tab route entries."""

    codes = tuple(
        row[0]
        for row in (
            APP_REGISTRATION_TAB_PAGES
            + MONITORING_TAB_PAGES
            + SERVICE_AUTH_TAB_PAGES
        )
    )

    codes_sql = ", ".join(f"'{code}'" for code in codes)

    op.execute(
        f"""
        DELETE FROM page_route_prefixes
        WHERE page_code IN ({codes_sql})
        """
    )

    op.execute(
        f"""
        DELETE FROM page_registry
        WHERE code IN ({codes_sql})
        """
    )
