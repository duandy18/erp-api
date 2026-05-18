"""user_permission_child_pages

Revision ID: 0019_user_permission_pages
Revises: 0018_service_auth_write_status
Create Date: 2026-05-18 15:30:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0019_user_permission_pages"
down_revision: str | Sequence[str] | None = "0018_service_auth_write_status"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


USER_PERMISSION_CHILD_PAGES = (
    (
        "erp.system.users.independent_system_user_permissions",
        "独立系统用户权限表",
        "/system/users",
        10,
    ),
    (
        "erp.system.users.permission_config",
        "用户权限配置表",
        "/system/users/permission-config",
        20,
    ),
)


def upgrade() -> None:
    """Register two third-level pages under 系统管理 / 用户与权限."""

    # 用户与权限作为侧边栏分组，不再直接承载业务页面。
    op.execute(
        """
        UPDATE page_registry
        SET
          name = '用户与权限',
          parent_code = 'erp.system',
          level = 2,
          domain_code = 'erp',
          show_in_topbar = FALSE,
          show_in_sidebar = TRUE,
          inherit_permissions = TRUE,
          read_permission_id = NULL,
          write_permission_id = NULL,
          sort_order = 10,
          is_active = TRUE
        WHERE code = 'erp.system.users'
        """
    )

    # 父级分组不占用 /system/users，真实业务路由交给子页面。
    op.execute(
        """
        DELETE FROM page_route_prefixes
        WHERE page_code = 'erp.system.users'
           OR page_code IN (
             'erp.system.users.independent_system_user_permissions',
             'erp.system.users.permission_config'
           )
           OR route_prefix IN (
             '/system/users',
             '/system/users/permission-config'
           )
        """
    )

    for page_code, page_name, _route_prefix, sort_order in USER_PERMISSION_CHILD_PAGES:
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
            VALUES (
              '{page_code}',
              '{page_name}',
              'erp.system.users',
              3,
              'erp',
              FALSE,
              TRUE,
              TRUE,
              NULL,
              NULL,
              {sort_order},
              TRUE
            )
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
              is_active = EXCLUDED.is_active
            """
        )

    for page_code, _page_name, route_prefix, sort_order in USER_PERMISSION_CHILD_PAGES:
        op.execute(
            f"""
            INSERT INTO page_route_prefixes (
              page_code,
              route_prefix,
              sort_order,
              is_active
            )
            VALUES (
              '{page_code}',
              '{route_prefix}',
              {sort_order},
              TRUE
            )
            """
        )


def downgrade() -> None:
    """Restore /system/users to the parent 用户与权限 page."""

    op.execute(
        """
        DELETE FROM page_route_prefixes
        WHERE page_code IN (
          'erp.system.users',
          'erp.system.users.independent_system_user_permissions',
          'erp.system.users.permission_config'
        )
           OR route_prefix IN (
             '/system/users',
             '/system/users/permission-config'
           )
        """
    )

    op.execute(
        """
        DELETE FROM page_registry
        WHERE code IN (
          'erp.system.users.independent_system_user_permissions',
          'erp.system.users.permission_config'
        )
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
          'erp.system.users',
          '/system/users',
          10,
          TRUE
        )
        """
    )
