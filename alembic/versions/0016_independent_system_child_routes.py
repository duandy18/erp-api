"""independent_system_child_routes

Revision ID: 0016_ind_sys_child_routes
Revises: 0015_ind_sys_parent_route
Create Date: 2026-05-18 11:10:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0016_ind_sys_child_routes"
down_revision: str | Sequence[str] | None = "0015_ind_sys_parent_route"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    # 独立系统注册作为侧边栏分组，不直接承载业务内容。
    op.execute(
        """
        UPDATE page_registry
        SET
          name = '独立系统注册',
          show_in_sidebar = TRUE,
          is_active = TRUE
        WHERE code = 'erp.system.apps'
        """
    )

    # 两个真实业务页面在左侧显示为独立子页面。
    op.execute(
        """
        UPDATE page_registry
        SET
          show_in_sidebar = TRUE,
          is_active = TRUE
        WHERE code IN (
          'erp.system.apps.independent_systems',
          'erp.system.apps.frontend_pages'
        )
        """
    )

    # 父分组不再拥有 /system/apps，避免与“独立系统列表”子页面抢同一路由。
    op.execute(
        """
        DELETE FROM page_route_prefixes
        WHERE page_code = 'erp.system.apps'
          AND route_prefix = '/system/apps'
        """
    )

    # /system/apps 归属“独立系统列表”。
    op.execute(
        """
        INSERT INTO page_route_prefixes (
          page_code,
          route_prefix,
          sort_order,
          is_active
        )
        VALUES (
          'erp.system.apps.independent_systems',
          '/system/apps',
          0,
          TRUE
        )
        ON CONFLICT (page_code, route_prefix) DO UPDATE
        SET
          sort_order = EXCLUDED.sort_order,
          is_active = EXCLUDED.is_active
        """
    )

    # /system/apps/frontend-pages 归属“独立系统前端页面目录”。
    op.execute(
        """
        INSERT INTO page_route_prefixes (
          page_code,
          route_prefix,
          sort_order,
          is_active
        )
        VALUES (
          'erp.system.apps.frontend_pages',
          '/system/apps/frontend-pages',
          10,
          TRUE
        )
        ON CONFLICT (page_code, route_prefix) DO UPDATE
        SET
          sort_order = EXCLUDED.sort_order,
          is_active = EXCLUDED.is_active
        """
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.execute(
        """
        DELETE FROM page_route_prefixes
        WHERE page_code = 'erp.system.apps.independent_systems'
          AND route_prefix = '/system/apps'
        """
    )

    op.execute(
        """
        INSERT INTO page_route_prefixes (
          page_code,
          route_prefix,
          sort_order,
          is_active
        )
        VALUES (
          'erp.system.apps',
          '/system/apps',
          0,
          TRUE
        )
        ON CONFLICT (page_code, route_prefix) DO UPDATE
        SET
          sort_order = EXCLUDED.sort_order,
          is_active = EXCLUDED.is_active
        """
    )

    op.execute(
        """
        UPDATE page_registry
        SET show_in_sidebar = FALSE
        WHERE code IN (
          'erp.system.apps.independent_systems',
          'erp.system.apps.frontend_pages'
        )
        """
    )
