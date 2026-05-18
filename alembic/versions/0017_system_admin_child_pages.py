"""system_admin_child_pages

Revision ID: 0017_system_child_pages
Revises: 0016_ind_sys_child_routes
Create Date: 2026-05-18 11:50:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0017_system_child_pages"
down_revision: str | Sequence[str] | None = "0016_ind_sys_child_routes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


SERVICE_AUTH_CHILD_PAGE_CODES = (
    "erp.system.service_auth.capabilities",
    "erp.system.service_auth.permissions",
    "erp.system.service_auth.write_status",
)

MONITORING_CHILD_PAGE_CODES = (
    "erp.system.monitoring.overview",
    "erp.system.monitoring.endpoints",
    "erp.system.monitoring.databases",
    "erp.system.monitoring.gateway",
    "erp.system.monitoring.dependencies",
    "erp.system.monitoring.service_auth",
    "erp.system.monitoring.openapi",
    "erp.system.monitoring.health",
)


def upgrade() -> None:
    """Upgrade schema."""

    # 父页作为左侧分组，不直接承载业务 route。
    op.execute(
        """
        UPDATE page_registry
        SET
          show_in_sidebar = TRUE,
          is_active = TRUE
        WHERE code IN (
          'erp.system.service_auth',
          'erp.system.monitoring'
        )
        """
    )

    # 系统协作配置与系统监控的 Tab 页面升级为真实侧边栏子页面。
    op.execute(
        """
        UPDATE page_registry
        SET
          show_in_sidebar = TRUE,
          is_active = TRUE
        WHERE code IN (
          'erp.system.service_auth.capabilities',
          'erp.system.service_auth.permissions',
          'erp.system.service_auth.write_status',
          'erp.system.monitoring.overview',
          'erp.system.monitoring.endpoints',
          'erp.system.monitoring.databases',
          'erp.system.monitoring.gateway',
          'erp.system.monitoring.dependencies',
          'erp.system.monitoring.service_auth',
          'erp.system.monitoring.openapi',
          'erp.system.monitoring.health'
        )
        """
    )

    # 删除父分组直接 route，避免父页和默认子页抢同一路径。
    op.execute(
        """
        DELETE FROM page_route_prefixes
        WHERE (page_code = 'erp.system.service_auth' AND route_prefix = '/system/service-auth')
           OR (page_code = 'erp.system.monitoring' AND route_prefix = '/system/monitoring')
        """
    )

    # 系统协作配置：能力目录承接 base route。
    op.execute(
        """
        INSERT INTO page_route_prefixes (
          page_code,
          route_prefix,
          sort_order,
          is_active
        )
        VALUES
          ('erp.system.service_auth.capabilities', '/system/service-auth', 0, TRUE),
          ('erp.system.service_auth.capabilities', '/system/service-auth/capabilities', 10, TRUE),
          ('erp.system.service_auth.permissions', '/system/service-auth/permissions', 20, TRUE),
          ('erp.system.service_auth.write_status', '/system/service-auth/write-status', 30, TRUE)
        ON CONFLICT (page_code, route_prefix) DO UPDATE
        SET
          sort_order = EXCLUDED.sort_order,
          is_active = EXCLUDED.is_active
        """
    )

    # 系统监控：应用运行总览承接 base route。
    op.execute(
        """
        INSERT INTO page_route_prefixes (
          page_code,
          route_prefix,
          sort_order,
          is_active
        )
        VALUES
          ('erp.system.monitoring.overview', '/system/monitoring', 0, TRUE),
          ('erp.system.monitoring.endpoints', '/system/monitoring/endpoints', 20, TRUE),
          ('erp.system.monitoring.databases', '/system/monitoring/databases', 30, TRUE),
          ('erp.system.monitoring.gateway', '/system/monitoring/gateway', 40, TRUE),
          ('erp.system.monitoring.dependencies', '/system/monitoring/dependencies', 50, TRUE),
          ('erp.system.monitoring.service_auth', '/system/monitoring/service-auth', 60, TRUE),
          ('erp.system.monitoring.openapi', '/system/monitoring/openapi', 70, TRUE),
          ('erp.system.monitoring.health', '/system/monitoring/health', 80, TRUE)
        ON CONFLICT (page_code, route_prefix) DO UPDATE
        SET
          sort_order = EXCLUDED.sort_order,
          is_active = EXCLUDED.is_active
        """
    )


def downgrade() -> None:
    """Downgrade schema."""

    # 回到上一阶段：这些页面存在于 page_registry，但不进入左侧菜单。
    op.execute(
        """
        UPDATE page_registry
        SET show_in_sidebar = FALSE
        WHERE code IN (
          'erp.system.service_auth.capabilities',
          'erp.system.service_auth.permissions',
          'erp.system.service_auth.write_status',
          'erp.system.monitoring.overview',
          'erp.system.monitoring.endpoints',
          'erp.system.monitoring.databases',
          'erp.system.monitoring.gateway',
          'erp.system.monitoring.dependencies',
          'erp.system.monitoring.service_auth',
          'erp.system.monitoring.openapi',
          'erp.system.monitoring.health'
        )
        """
    )

    # 移除新增给能力目录的 base route。
    op.execute(
        """
        DELETE FROM page_route_prefixes
        WHERE page_code = 'erp.system.service_auth.capabilities'
          AND route_prefix = '/system/service-auth'
        """
    )

    # 恢复父页 base routes。
    op.execute(
        """
        INSERT INTO page_route_prefixes (
          page_code,
          route_prefix,
          sort_order,
          is_active
        )
        VALUES
          ('erp.system.service_auth', '/system/service-auth', 0, TRUE),
          ('erp.system.monitoring', '/system/monitoring', 0, TRUE)
        ON CONFLICT (page_code, route_prefix) DO UPDATE
        SET
          sort_order = EXCLUDED.sort_order,
          is_active = EXCLUDED.is_active
        """
    )
