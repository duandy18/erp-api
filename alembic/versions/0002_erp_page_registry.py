"""erp_page_registry

Revision ID: 0002_erp_page_registry
Revises: 0001_erp_baseline
Create Date: 2026-05-15 18:20:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_erp_page_registry"
down_revision: str | Sequence[str] | None = "0001_erp_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_permissions"),
        sa.UniqueConstraint("name", name="uq_permissions_name"),
    )

    op.create_table(
        "page_registry",
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("parent_code", sa.String(length=128), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("domain_code", sa.String(length=64), nullable=False),
        sa.Column("show_in_topbar", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("show_in_sidebar", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "inherit_permissions", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column("read_permission_id", sa.Integer(), nullable=True),
        sa.Column("write_permission_id", sa.Integer(), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("level >= 1", name="ck_page_registry_level_positive"),
        sa.CheckConstraint("length(trim(code)) > 0", name="ck_page_registry_code_non_empty"),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_page_registry_name_non_empty"),
        sa.CheckConstraint(
            "length(trim(domain_code)) > 0", name="ck_page_registry_domain_code_non_empty"
        ),
        sa.ForeignKeyConstraint(
            ["parent_code"],
            ["page_registry.code"],
            name="fk_page_registry_parent_code_page_registry",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["read_permission_id"],
            ["permissions.id"],
            name="fk_page_registry_read_permission_id_permissions",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["write_permission_id"],
            ["permissions.id"],
            name="fk_page_registry_write_permission_id_permissions",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("code", name="pk_page_registry"),
    )
    op.create_index("ix_page_registry_parent_code", "page_registry", ["parent_code"])
    op.create_index(
        "ix_page_registry_domain_level_sort",
        "page_registry",
        ["domain_code", "level", "sort_order"],
    )

    op.create_table(
        "page_route_prefixes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("page_code", sa.String(length=128), nullable=False),
        sa.Column("route_prefix", sa.String(length=256), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(route_prefix)) > 0",
            name="ck_page_route_prefixes_route_prefix_non_empty",
        ),
        sa.ForeignKeyConstraint(
            ["page_code"],
            ["page_registry.code"],
            name="fk_page_route_prefixes_page_code_page_registry",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_page_route_prefixes"),
        sa.UniqueConstraint("page_code", "route_prefix", name="uq_page_route_prefixes_page_route"),
    )
    op.create_index("ix_page_route_prefixes_page_code", "page_route_prefixes", ["page_code"])

    op.execute(
        """
        INSERT INTO permissions (name)
        VALUES
          ('page.erp.portal.read'),
          ('page.erp.portal.write'),
          ('page.erp.apps.read'),
          ('page.erp.apps.write'),
          ('page.erp.cockpit.read'),
          ('page.erp.cockpit.write'),
          ('page.erp.system.read'),
          ('page.erp.system.write')
        ON CONFLICT (name) DO NOTHING
        """
    )

    op.execute(
        """
        INSERT INTO page_registry (
          code, name, parent_code, level, domain_code,
          show_in_topbar, show_in_sidebar, inherit_permissions,
          read_permission_id, write_permission_id, sort_order, is_active
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
            'erp.apps',
            '应用中心',
            NULL,
            1,
            'erp',
            TRUE,
            TRUE,
            FALSE,
            (SELECT id FROM permissions WHERE name = 'page.erp.apps.read'),
            (SELECT id FROM permissions WHERE name = 'page.erp.apps.write'),
            20,
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
          ),
          (
            'erp.system',
            '系统管理',
            NULL,
            1,
            'erp',
            TRUE,
            TRUE,
            FALSE,
            (SELECT id FROM permissions WHERE name = 'page.erp.system.read'),
            (SELECT id FROM permissions WHERE name = 'page.erp.system.write'),
            90,
            TRUE
          )
        """
    )

    op.execute(
        """
        INSERT INTO page_registry (
          code, name, parent_code, level, domain_code,
          show_in_topbar, show_in_sidebar, inherit_permissions,
          read_permission_id, write_permission_id, sort_order, is_active
        )
        VALUES
          (
            'erp.system.users',
            '用户管理',
            'erp.system',
            2,
            'erp',
            FALSE,
            TRUE,
            TRUE,
            NULL,
            NULL,
            10,
            TRUE
          )
        """
    )

    op.execute(
        """
        INSERT INTO page_route_prefixes (page_code, route_prefix)
        VALUES
          ('erp.portal', '/'),
          ('erp.apps', '/apps'),
          ('erp.cockpit', '/cockpit'),
          ('erp.system.users', '/system/users')
        ON CONFLICT (page_code, route_prefix) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index("ix_page_route_prefixes_page_code", table_name="page_route_prefixes")
    op.drop_table("page_route_prefixes")
    op.drop_index("ix_page_registry_domain_level_sort", table_name="page_registry")
    op.drop_index("ix_page_registry_parent_code", table_name="page_registry")
    op.drop_table("page_registry")
    op.drop_table("permissions")
