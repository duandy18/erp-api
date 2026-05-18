"""service_auth_write_status

Revision ID: 0018_service_auth_write_status
Revises: 0017_system_child_pages
Create Date: 2026-05-18 13:20:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0018_service_auth_write_status"
down_revision: str | Sequence[str] | None = "0017_system_child_pages"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "app_registry_service_permission_write_runs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.Column("source_app_code", sa.String(length=64), nullable=False),
        sa.Column("target_app_code", sa.String(length=64), nullable=False),
        sa.Column("client_code", sa.String(length=64), nullable=True),
        sa.Column("permission_code", sa.String(length=128), nullable=False),
        sa.Column("operation", sa.String(length=32), server_default="upsert", nullable=False),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("target_base_url", sa.String(length=255), nullable=True),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("raw_excerpt", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["app_registry_service_permissions.id"],
            name="fk_app_registry_service_permission_write_runs_permission_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_service_permission_write_runs"),
        sa.CheckConstraint(
            "operation IN ('upsert', 'disable', 'verify')",
            name="ck_svc_perm_write_runs_operation",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'success', 'failure', 'skipped')",
            name="ck_svc_perm_write_runs_status",
        ),
        sa.CheckConstraint(
            "length(trim(source_app_code)) > 0",
            name="ck_svc_perm_write_runs_source",
        ),
        sa.CheckConstraint(
            "length(trim(target_app_code)) > 0",
            name="ck_svc_perm_write_runs_target",
        ),
        sa.CheckConstraint(
            "length(trim(permission_code)) > 0",
            name="ck_svc_perm_write_runs_permission",
        ),
        sa.CheckConstraint(
            "http_status IS NULL OR http_status > 0",
            name="ck_svc_perm_write_runs_http_status",
        ),
    )
    op.create_index(
        "ix_app_registry_service_permission_write_runs_permission_id",
        "app_registry_service_permission_write_runs",
        ["permission_id"],
    )
    op.create_index(
        "ix_app_registry_service_permission_write_runs_target_status",
        "app_registry_service_permission_write_runs",
        ["target_app_code", "status"],
    )
    op.create_index(
        "ix_app_registry_service_permission_write_runs_started_at",
        "app_registry_service_permission_write_runs",
        ["started_at"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_app_registry_service_permission_write_runs_started_at",
        table_name="app_registry_service_permission_write_runs",
    )
    op.drop_index(
        "ix_app_registry_service_permission_write_runs_target_status",
        table_name="app_registry_service_permission_write_runs",
    )
    op.drop_index(
        "ix_app_registry_service_permission_write_runs_permission_id",
        table_name="app_registry_service_permission_write_runs",
    )
    op.drop_table("app_registry_service_permission_write_runs")
