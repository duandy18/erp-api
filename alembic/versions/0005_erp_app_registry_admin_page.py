"""erp_app_registry_admin_page

Revision ID: 0005_erp_app_registry_admin_page
Revises: 0004_erp_app_registry
Create Date: 2026-05-15 21:20:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0005_erp_app_registry_admin_page"
down_revision: str | Sequence[str] | None = "0004_erp_app_registry"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
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
        VALUES (
          'erp.system.apps',
          '应用注册',
          'erp.system',
          2,
          'erp',
          FALSE,
          TRUE,
          TRUE,
          NULL,
          NULL,
          20,
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

    op.execute(
        """
        INSERT INTO page_route_prefixes (page_code, route_prefix)
        VALUES ('erp.system.apps', '/system/apps')
        ON CONFLICT (page_code, route_prefix) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM page_route_prefixes
        WHERE page_code = 'erp.system.apps'
          AND route_prefix = '/system/apps'
        """
    )
    op.execute(
        """
        DELETE FROM page_registry
        WHERE code = 'erp.system.apps'
        """
    )
