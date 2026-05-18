"""app_registry_iam_projection

Revision ID: 0020_app_registry_iam_projection
Revises: 0019_user_permission_pages
Create Date: 2026-05-18 15:45:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0020_app_registry_iam_projection"
down_revision: str | Sequence[str] | None = "0019_user_permission_pages"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "app_registry_iam_sync_runs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("source_base_url", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="running", nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_snapshot_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fetched_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("inserted_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("updated_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("deleted_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("raw_excerpt", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_reg_iam_sync_runs_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_iam_sync_runs"),
        sa.CheckConstraint(
            "status IN ('running', 'success', 'failure')",
            name="ck_app_reg_iam_sync_runs_status",
        ),
        sa.CheckConstraint(
            "fetched_count >= 0 "
            "AND inserted_count >= 0 "
            "AND updated_count >= 0 "
            "AND deleted_count >= 0",
            name="ck_app_reg_iam_sync_runs_counts",
        ),
    )
    op.create_index(
        "ix_app_reg_iam_sync_runs_app_code",
        "app_registry_iam_sync_runs",
        ["app_code"],
    )
    op.create_index(
        "ix_app_reg_iam_sync_runs_started_at",
        "app_registry_iam_sync_runs",
        ["started_at"],
    )
    op.create_index(
        "ix_app_reg_iam_sync_runs_status",
        "app_registry_iam_sync_runs",
        ["status"],
    )

    op.create_table(
        "app_registry_iam_user_projection",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("source_user_id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("last_sync_run_id", sa.BigInteger(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_reg_iam_user_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["last_sync_run_id"],
            ["app_registry_iam_sync_runs.id"],
            name="fk_app_reg_iam_user_sync_run",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_iam_user_projection"),
        sa.UniqueConstraint(
            "app_code",
            "source_user_id",
            name="uq_app_reg_iam_user_app_source_user",
        ),
        sa.CheckConstraint(
            "source_user_id > 0",
            name="ck_app_reg_iam_user_source_user_positive",
        ),
        sa.CheckConstraint(
            "btrim(username) <> ''",
            name="ck_app_reg_iam_user_username_non_empty",
        ),
    )
    op.create_index(
        "ix_app_reg_iam_user_app_code",
        "app_registry_iam_user_projection",
        ["app_code"],
    )
    op.create_index(
        "ix_app_reg_iam_user_username",
        "app_registry_iam_user_projection",
        ["username"],
    )

    op.create_table(
        "app_registry_iam_permission_projection",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("source_permission_id", sa.Integer(), nullable=False),
        sa.Column("permission_code", sa.String(length=255), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("last_sync_run_id", sa.BigInteger(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_reg_iam_perm_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["last_sync_run_id"],
            ["app_registry_iam_sync_runs.id"],
            name="fk_app_reg_iam_perm_sync_run",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_iam_permission_projection"),
        sa.UniqueConstraint(
            "app_code",
            "permission_code",
            name="uq_app_reg_iam_perm_app_code",
        ),
        sa.CheckConstraint(
            "source_permission_id > 0",
            name="ck_app_reg_iam_perm_source_positive",
        ),
        sa.CheckConstraint(
            "btrim(permission_code) <> ''",
            name="ck_app_reg_iam_perm_code_non_empty",
        ),
    )
    op.create_index(
        "ix_app_reg_iam_perm_app_code",
        "app_registry_iam_permission_projection",
        ["app_code"],
    )

    op.create_table(
        "app_registry_iam_user_permission_projection",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("source_user_id", sa.Integer(), nullable=False),
        sa.Column("source_permission_id", sa.Integer(), nullable=False),
        sa.Column("permission_code", sa.String(length=255), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("last_sync_run_id", sa.BigInteger(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_reg_iam_user_perm_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["last_sync_run_id"],
            ["app_registry_iam_sync_runs.id"],
            name="fk_app_reg_iam_user_perm_sync_run",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_app_registry_iam_user_permission_projection",
        ),
        sa.UniqueConstraint(
            "app_code",
            "source_user_id",
            "permission_code",
            name="uq_app_reg_iam_user_perm_identity",
        ),
        sa.CheckConstraint(
            "source_user_id > 0",
            name="ck_app_reg_iam_user_perm_user_positive",
        ),
        sa.CheckConstraint(
            "source_permission_id > 0",
            name="ck_app_reg_iam_user_perm_perm_positive",
        ),
        sa.CheckConstraint(
            "btrim(permission_code) <> ''",
            name="ck_app_reg_iam_user_perm_code_non_empty",
        ),
    )
    op.create_index(
        "ix_app_reg_iam_user_perm_app_code",
        "app_registry_iam_user_permission_projection",
        ["app_code"],
    )
    op.create_index(
        "ix_app_reg_iam_user_perm_user",
        "app_registry_iam_user_permission_projection",
        ["app_code", "source_user_id"],
    )

    op.create_table(
        "app_registry_iam_page_projection",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("page_code", sa.String(length=128), nullable=False),
        sa.Column("page_name", sa.String(length=128), nullable=False),
        sa.Column("parent_page_code", sa.String(length=128), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("domain_code", sa.String(length=64), nullable=True),
        sa.Column(
            "show_in_topbar",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "show_in_sidebar",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "inherit_permissions",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("read_permission_code", sa.String(length=255), nullable=True),
        sa.Column("write_permission_code", sa.String(length=255), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("last_sync_run_id", sa.BigInteger(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_reg_iam_page_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["last_sync_run_id"],
            ["app_registry_iam_sync_runs.id"],
            name="fk_app_reg_iam_page_sync_run",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_iam_page_projection"),
        sa.UniqueConstraint(
            "app_code",
            "page_code",
            name="uq_app_reg_iam_page_app_page",
        ),
        sa.CheckConstraint(
            "btrim(page_code) <> ''",
            name="ck_app_reg_iam_page_code_non_empty",
        ),
        sa.CheckConstraint(
            "btrim(page_name) <> ''",
            name="ck_app_reg_iam_page_name_non_empty",
        ),
        sa.CheckConstraint(
            "level >= 1",
            name="ck_app_reg_iam_page_level_positive",
        ),
    )
    op.create_index(
        "ix_app_reg_iam_page_app_code",
        "app_registry_iam_page_projection",
        ["app_code"],
    )
    op.create_index(
        "ix_app_reg_iam_page_parent",
        "app_registry_iam_page_projection",
        ["app_code", "parent_page_code"],
    )

    op.create_table(
        "app_registry_iam_page_route_prefix_projection",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("page_code", sa.String(length=128), nullable=False),
        sa.Column("route_prefix", sa.String(length=255), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("last_sync_run_id", sa.BigInteger(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_reg_iam_route_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["last_sync_run_id"],
            ["app_registry_iam_sync_runs.id"],
            name="fk_app_reg_iam_route_sync_run",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_app_registry_iam_page_route_prefix_projection",
        ),
        sa.UniqueConstraint(
            "app_code",
            "page_code",
            "route_prefix",
            name="uq_app_reg_iam_route_prefix_identity",
        ),
        sa.CheckConstraint(
            "btrim(page_code) <> ''",
            name="ck_app_reg_iam_route_page_code_non_empty",
        ),
        sa.CheckConstraint(
            "btrim(route_prefix) <> ''",
            name="ck_app_reg_iam_route_prefix_non_empty",
        ),
    )
    op.create_index(
        "ix_app_reg_iam_route_app_code",
        "app_registry_iam_page_route_prefix_projection",
        ["app_code"],
    )
    op.create_index(
        "ix_app_reg_iam_route_page",
        "app_registry_iam_page_route_prefix_projection",
        ["app_code", "page_code"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_app_reg_iam_route_page",
        table_name="app_registry_iam_page_route_prefix_projection",
    )
    op.drop_index(
        "ix_app_reg_iam_route_app_code",
        table_name="app_registry_iam_page_route_prefix_projection",
    )
    op.drop_table("app_registry_iam_page_route_prefix_projection")

    op.drop_index(
        "ix_app_reg_iam_page_parent",
        table_name="app_registry_iam_page_projection",
    )
    op.drop_index(
        "ix_app_reg_iam_page_app_code",
        table_name="app_registry_iam_page_projection",
    )
    op.drop_table("app_registry_iam_page_projection")

    op.drop_index(
        "ix_app_reg_iam_user_perm_user",
        table_name="app_registry_iam_user_permission_projection",
    )
    op.drop_index(
        "ix_app_reg_iam_user_perm_app_code",
        table_name="app_registry_iam_user_permission_projection",
    )
    op.drop_table("app_registry_iam_user_permission_projection")

    op.drop_index(
        "ix_app_reg_iam_perm_app_code",
        table_name="app_registry_iam_permission_projection",
    )
    op.drop_table("app_registry_iam_permission_projection")

    op.drop_index(
        "ix_app_reg_iam_user_username",
        table_name="app_registry_iam_user_projection",
    )
    op.drop_index(
        "ix_app_reg_iam_user_app_code",
        table_name="app_registry_iam_user_projection",
    )
    op.drop_table("app_registry_iam_user_projection")

    op.drop_index(
        "ix_app_reg_iam_sync_runs_status",
        table_name="app_registry_iam_sync_runs",
    )
    op.drop_index(
        "ix_app_reg_iam_sync_runs_started_at",
        table_name="app_registry_iam_sync_runs",
    )
    op.drop_index(
        "ix_app_reg_iam_sync_runs_app_code",
        table_name="app_registry_iam_sync_runs",
    )
    op.drop_table("app_registry_iam_sync_runs")
