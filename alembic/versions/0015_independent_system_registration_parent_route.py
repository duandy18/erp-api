"""independent_system_registration_parent_route

Revision ID: 0015_ind_sys_parent_route
Revises: 0014_independent_system_pages
Create Date: 2026-05-18 10:30:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0015_ind_sys_parent_route"
down_revision: str | Sequence[str] | None = "0014_independent_system_pages"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    # 独立系统注册是左侧可见父入口，父入口必须拥有 /system/apps。
    # 否则 AppShell 只能把 erp.system.apps 渲染成不可点击标题。
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

    # 两个子页面作为父页面内部内容页，不额外增加左侧菜单入口。
    op.execute(
        """
        UPDATE page_registry
        SET
          show_in_sidebar = FALSE,
          is_active = TRUE
        WHERE code IN (
          'erp.system.apps.independent_systems',
          'erp.system.apps.frontend_pages'
        )
        """
    )

    # /system/apps 归属可见父页 erp.system.apps。
    # 先移除错误挂到子页上的同一路由，避免左侧父入口无 route。
    op.execute(
        """
        DELETE FROM page_route_prefixes
        WHERE route_prefix = '/system/apps'
          AND page_code <> 'erp.system.apps'
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

    # 页面目录仍然是独立子路由，但不新增左侧菜单入口。
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
        WHERE page_code = 'erp.system.apps'
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
