"""independent_system_registration_pages

Revision ID: 0014_independent_system_pages
Revises: 0013_app_registry_self_desc
Create Date: 2026-05-17
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0014_independent_system_pages"
down_revision: str | Sequence[str] | None = "0013_app_registry_self_desc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "page_route_prefixes",
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "page_route_prefixes",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_page_route_prefixes_is_active",
        "page_route_prefixes",
        ["is_active"],
    )

    op.execute(
        """
        UPDATE page_registry
        SET name = '独立系统注册'
        WHERE code = 'erp.system.apps';
        """
    )

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
            is_active,
            sort_order
        )
        VALUES
            (
                'erp.system.apps.independent_systems',
                '独立系统列表',
                'erp.system.apps',
                3,
                'erp',
                FALSE,
                FALSE,
                TRUE,
                NULL,
                NULL,
                TRUE,
                10
            ),
            (
                'erp.system.apps.frontend_pages',
                '独立系统前端页面目录',
                'erp.system.apps',
                3,
                'erp',
                FALSE,
                FALSE,
                TRUE,
                NULL,
                NULL,
                TRUE,
                20
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
            is_active = EXCLUDED.is_active,
            sort_order = EXCLUDED.sort_order;
        """
    )

    op.execute(
        """
        DELETE FROM page_route_prefixes
        WHERE route_prefix IN (
            '/system/apps',
            '/system/apps/frontend-pages',
            '/system/apps/components',
            '/system/apps/environments',
            '/system/apps/app-environments',
            '/system/apps/repositories',
            '/system/apps/gateway'
        );

        INSERT INTO page_route_prefixes (
            page_code,
            route_prefix,
            sort_order,
            is_active
        )
        VALUES
            (
                'erp.system.apps.independent_systems',
                '/system/apps',
                10,
                TRUE
            ),
            (
                'erp.system.apps.frontend_pages',
                '/system/apps/frontend-pages',
                20,
                TRUE
            );
        """
    )

    op.execute(
        """
        DELETE FROM page_registry
        WHERE code IN (
            'erp.system.apps.basic',
            'erp.system.apps.components',
            'erp.system.apps.environments',
            'erp.system.apps.app_environments',
            'erp.system.apps.repositories',
            'erp.system.apps.gateway'
        );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE page_registry
        SET name = '应用注册'
        WHERE code = 'erp.system.apps';
        """
    )

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
            is_active,
            sort_order
        )
        VALUES
            (
                'erp.system.apps.basic',
                '基础信息',
                'erp.system.apps',
                3,
                'erp',
                FALSE,
                FALSE,
                TRUE,
                NULL,
                NULL,
                TRUE,
                10
            ),
            (
                'erp.system.apps.components',
                '组件',
                'erp.system.apps',
                3,
                'erp',
                FALSE,
                FALSE,
                TRUE,
                NULL,
                NULL,
                TRUE,
                20
            ),
            (
                'erp.system.apps.environments',
                '环境',
                'erp.system.apps',
                3,
                'erp',
                FALSE,
                FALSE,
                TRUE,
                NULL,
                NULL,
                TRUE,
                30
            ),
            (
                'erp.system.apps.app_environments',
                '应用环境',
                'erp.system.apps',
                3,
                'erp',
                FALSE,
                FALSE,
                TRUE,
                NULL,
                NULL,
                TRUE,
                40
            ),
            (
                'erp.system.apps.repositories',
                '仓库',
                'erp.system.apps',
                3,
                'erp',
                FALSE,
                FALSE,
                TRUE,
                NULL,
                NULL,
                TRUE,
                50
            ),
            (
                'erp.system.apps.gateway',
                'Gateway 配置',
                'erp.system.apps',
                3,
                'erp',
                FALSE,
                FALSE,
                TRUE,
                NULL,
                NULL,
                TRUE,
                60
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
            is_active = EXCLUDED.is_active,
            sort_order = EXCLUDED.sort_order;
        """
    )

    op.execute(
        """
        DELETE FROM page_route_prefixes
        WHERE route_prefix IN (
            '/system/apps',
            '/system/apps/frontend-pages',
            '/system/apps/components',
            '/system/apps/environments',
            '/system/apps/app-environments',
            '/system/apps/repositories',
            '/system/apps/gateway'
        );

        INSERT INTO page_route_prefixes (
            page_code,
            route_prefix,
            sort_order,
            is_active
        )
        VALUES
            (
                'erp.system.apps.basic',
                '/system/apps',
                10,
                TRUE
            ),
            (
                'erp.system.apps.components',
                '/system/apps/components',
                20,
                TRUE
            ),
            (
                'erp.system.apps.environments',
                '/system/apps/environments',
                30,
                TRUE
            ),
            (
                'erp.system.apps.app_environments',
                '/system/apps/app-environments',
                40,
                TRUE
            ),
            (
                'erp.system.apps.repositories',
                '/system/apps/repositories',
                50,
                TRUE
            ),
            (
                'erp.system.apps.gateway',
                '/system/apps/gateway',
                60,
                TRUE
            );
        """
    )

    op.execute(
        """
        DELETE FROM page_registry
        WHERE code IN (
            'erp.system.apps.independent_systems',
            'erp.system.apps.frontend_pages'
        );
        """
    )

    op.drop_index(
        "ix_page_route_prefixes_is_active",
        table_name="page_route_prefixes",
    )
    op.drop_column("page_route_prefixes", "is_active")
    op.drop_column("page_route_prefixes", "sort_order")
