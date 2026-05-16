"""erp_control_plane_page_registry

Revision ID: 0010_erp_control_plane_page_registry
Revises: 0009_app_registry_runtime_governance
Create Date: 2026-05-16 21:45:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0010_erp_pages"
down_revision: str | Sequence[str] | None = "0009_app_registry_ops"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


RETIRED_PAGE_CODES = (
    "erp.portal",
    "erp.cockpit",
    "erp.system.audit",
)

RETIRED_PERMISSION_NAMES = (
    "page.erp.portal.read",
    "page.erp.portal.write",
    "page.erp.cockpit.read",
    "page.erp.cockpit.write",
    "page.erp.audit.read",
    "page.erp.audit.write",
    "page.erp.system.audit.read",
    "page.erp.system.audit.write",
)


def upgrade() -> None:
    """收口 ERP 页面注册结构。

    目标页面结构：

    ERP 总控平台
    ├── 我的应用
    └── 系统管理
        ├── 用户与权限
        ├── 应用注册
        ├── 系统协作配置
        └── 系统监控

    说明：
    - 我的应用复用既有 erp.apps / page.erp.apps.*，避免新增权限列。
    - 系统管理下二级页面继续继承 page.erp.system.*。
    - 退役总控首页和总控驾驶舱，避免 ERP 首页发散。
    """

    # 1) 先删除退役页面。page_route_prefixes 对 page_registry 是 ON DELETE CASCADE。
    op.execute(
        """
        DELETE FROM page_registry
        WHERE code IN (
          'erp.portal',
          'erp.cockpit',
          'erp.system.audit'
        )
        """
    )

    # 2) 再删除退役权限。user_permissions 对 permissions 是 ON DELETE CASCADE。
    op.execute(
        """
        DELETE FROM permissions
        WHERE name IN (
          'page.erp.portal.read',
          'page.erp.portal.write',
          'page.erp.cockpit.read',
          'page.erp.cockpit.write',
          'page.erp.audit.read',
          'page.erp.audit.write',
          'page.erp.system.audit.read',
          'page.erp.system.audit.write'
        )
        """
    )

    # 3) erp.apps 收口为“我的应用”，作为登录后默认入口。
    op.execute(
        """
        UPDATE page_registry
        SET
          name = '我的应用',
          parent_code = NULL,
          level = 1,
          domain_code = 'erp',
          show_in_topbar = TRUE,
          show_in_sidebar = TRUE,
          inherit_permissions = FALSE,
          read_permission_id = (SELECT id FROM permissions WHERE name = 'page.erp.apps.read'),
          write_permission_id = (SELECT id FROM permissions WHERE name = 'page.erp.apps.write'),
          sort_order = 10,
          is_active = TRUE,
          updated_at = now()
        WHERE code = 'erp.apps'
        """
    )

    # 4) 系统管理作为唯一管理入口。
    op.execute(
        """
        UPDATE page_registry
        SET
          name = '系统管理',
          parent_code = NULL,
          level = 1,
          domain_code = 'erp',
          show_in_topbar = TRUE,
          show_in_sidebar = TRUE,
          inherit_permissions = FALSE,
          read_permission_id = (SELECT id FROM permissions WHERE name = 'page.erp.system.read'),
          write_permission_id = (SELECT id FROM permissions WHERE name = 'page.erp.system.write'),
          sort_order = 90,
          is_active = TRUE,
          updated_at = now()
        WHERE code = 'erp.system'
        """
    )

    # 5) 系统管理下既有子页命名收口。
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
          is_active = TRUE,
          updated_at = now()
        WHERE code = 'erp.system.users'
        """
    )

    op.execute(
        """
        UPDATE page_registry
        SET
          name = '应用注册',
          parent_code = 'erp.system',
          level = 2,
          domain_code = 'erp',
          show_in_topbar = FALSE,
          show_in_sidebar = TRUE,
          inherit_permissions = TRUE,
          read_permission_id = NULL,
          write_permission_id = NULL,
          sort_order = 20,
          is_active = TRUE,
          updated_at = now()
        WHERE code = 'erp.system.apps'
        """
    )

    # 6) 新增系统管理下两个二级页，均继承 erp.system 权限。
    op.execute(
        """
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
          (
            'erp.system.service_auth',
            '系统协作配置',
            'erp.system',
            2,
            'erp',
            FALSE,
            TRUE,
            TRUE,
            NULL,
            NULL,
            30,
            TRUE
          ),
          (
            'erp.system.monitoring',
            '系统监控',
            'erp.system',
            2,
            'erp',
            FALSE,
            TRUE,
            TRUE,
            NULL,
            NULL,
            40,
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
          is_active = EXCLUDED.is_active,
          updated_at = now()
        """
    )

    # 7) 路由前缀收口：我的应用占用 /，不再把 / 交给总控首页。
    op.execute(
        """
        DELETE FROM page_route_prefixes
        WHERE page_code IN (
          'erp.portal',
          'erp.cockpit',
          'erp.system.audit'
        )
           OR route_prefix IN (
          '/cockpit',
          '/system/audit'
        )
        """
    )

    op.execute(
        """
        DELETE FROM page_route_prefixes
        WHERE page_code = 'erp.apps'
          AND route_prefix = '/apps'
        """
    )

    op.execute(
        """
        INSERT INTO page_route_prefixes (page_code, route_prefix)
        VALUES
          ('erp.apps', '/'),
          ('erp.system.users', '/system/users'),
          ('erp.system.apps', '/system/apps'),
          ('erp.system.service_auth', '/system/service-auth'),
          ('erp.system.monitoring', '/system/monitoring')
        ON CONFLICT (page_code, route_prefix) DO NOTHING
        """
    )


def downgrade() -> None:
    """恢复迁移前的页面注册结构。

    注意：
    upgrade 删除 retired permissions 时会级联清理 user_permissions；
    downgrade 只近似恢复 admin 用户的基础权限，不尝试恢复所有历史用户授权。
    """

    # 1) 删除新增路由和新增页面。
    op.execute(
        """
        DELETE FROM page_route_prefixes
        WHERE page_code IN (
          'erp.system.service_auth',
          'erp.system.monitoring'
        )
        """
    )

    op.execute(
        """
        DELETE FROM page_registry
        WHERE code IN (
          'erp.system.service_auth',
          'erp.system.monitoring'
        )
        """
    )

    # 2) 恢复退役权限定义。
    op.execute(
        """
        INSERT INTO permissions (name)
        VALUES
          ('page.erp.portal.read'),
          ('page.erp.portal.write'),
          ('page.erp.cockpit.read'),
          ('page.erp.cockpit.write')
        ON CONFLICT (name) DO NOTHING
        """
    )

    # 3) 恢复总控首页和总控驾驶舱。
    op.execute(
        """
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
          (
            'erp.portal',
            '总控首页',
            NULL,
            1,
            'erp',
            TRUE,
            TRUE,
            FALSE,
            (SELECT id FROM permissions WHERE name = 'page.erp.portal.read'),
            (SELECT id FROM permissions WHERE name = 'page.erp.portal.write'),
            10,
            TRUE
          ),
          (
            'erp.cockpit',
            '总控驾驶舱',
            NULL,
            1,
            'erp',
            TRUE,
            TRUE,
            FALSE,
            (SELECT id FROM permissions WHERE name = 'page.erp.cockpit.read'),
            (SELECT id FROM permissions WHERE name = 'page.erp.cockpit.write'),
            30,
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
          is_active = EXCLUDED.is_active,
          updated_at = now()
        """
    )

    # 4) 恢复应用中心和系统管理原命名/排序。
    op.execute(
        """
        UPDATE page_registry
        SET
          name = '应用中心',
          parent_code = NULL,
          level = 1,
          domain_code = 'erp',
          show_in_topbar = TRUE,
          show_in_sidebar = TRUE,
          inherit_permissions = FALSE,
          read_permission_id = (SELECT id FROM permissions WHERE name = 'page.erp.apps.read'),
          write_permission_id = (SELECT id FROM permissions WHERE name = 'page.erp.apps.write'),
          sort_order = 20,
          is_active = TRUE,
          updated_at = now()
        WHERE code = 'erp.apps'
        """
    )

    op.execute(
        """
        UPDATE page_registry
        SET
          name = '系统管理',
          parent_code = NULL,
          level = 1,
          domain_code = 'erp',
          show_in_topbar = TRUE,
          show_in_sidebar = TRUE,
          inherit_permissions = FALSE,
          read_permission_id = (SELECT id FROM permissions WHERE name = 'page.erp.system.read'),
          write_permission_id = (SELECT id FROM permissions WHERE name = 'page.erp.system.write'),
          sort_order = 90,
          is_active = TRUE,
          updated_at = now()
        WHERE code = 'erp.system'
        """
    )

    op.execute(
        """
        UPDATE page_registry
        SET
          name = '用户管理',
          parent_code = 'erp.system',
          level = 2,
          domain_code = 'erp',
          show_in_topbar = FALSE,
          show_in_sidebar = TRUE,
          inherit_permissions = TRUE,
          read_permission_id = NULL,
          write_permission_id = NULL,
          sort_order = 10,
          is_active = TRUE,
          updated_at = now()
        WHERE code = 'erp.system.users'
        """
    )

    # 5) 恢复旧路由前缀。
    op.execute(
        """
        DELETE FROM page_route_prefixes
        WHERE page_code = 'erp.apps'
          AND route_prefix = '/'
        """
    )

    op.execute(
        """
        INSERT INTO page_route_prefixes (page_code, route_prefix)
        VALUES
          ('erp.portal', '/'),
          ('erp.apps', '/apps'),
          ('erp.cockpit', '/cockpit'),
          ('erp.system.users', '/system/users'),
          ('erp.system.apps', '/system/apps')
        ON CONFLICT (page_code, route_prefix) DO NOTHING
        """
    )

    # 6) 近似恢复 admin 用户的旧权限。
    op.execute(
        """
        INSERT INTO user_permissions (user_id, permission_id)
        SELECT u.id, p.id
        FROM users u
        CROSS JOIN permissions p
        WHERE u.username = 'admin'
          AND p.name IN (
            'page.erp.portal.read',
            'page.erp.portal.write',
            'page.erp.cockpit.read',
            'page.erp.cockpit.write'
          )
        ON CONFLICT (user_id, permission_id) DO NOTHING
        """
    )
