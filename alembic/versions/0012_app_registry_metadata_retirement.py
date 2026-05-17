"""retire_app_registry_metadata_tables

Revision ID: 0012_app_meta_retire
Revises: 0011_erp_tabs
Create Date: 2026-05-17 11:55:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0012_app_meta_retire"
down_revision: str | Sequence[str] | None = "0011_erp_tabs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    # Retire metadata-only tables that no longer back ERP App Registry UI.
    op.drop_table("app_registry_repositories")
    op.drop_table("app_registry_app_environments")

    # Keep endpoints for monitoring, but remove component coupling.
    op.drop_constraint(
        "fk_app_registry_endpoints_component_id_components",
        "app_registry_endpoints",
        type_="foreignkey",
    )
    op.drop_column("app_registry_endpoints", "component_id")

    # Keep env_code as a plain label for monitoring/config views.
    op.drop_constraint(
        "fk_app_registry_endpoints_env_code_environments",
        "app_registry_endpoints",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_app_registry_databases_env_code_environments",
        "app_registry_databases",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_app_registry_gateway_bindings_env_code_environments",
        "app_registry_gateway_bindings",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_app_registry_health_checks_env_code_environments",
        "app_registry_health_checks",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_app_registry_openapi_sources_env_code_environments",
        "app_registry_openapi_sources",
        type_="foreignkey",
    )

    op.drop_table("app_registry_components")
    op.drop_table("app_registry_environments")


def downgrade() -> None:
    """Downgrade schema."""

    op.create_table(
        "app_registry_environments",
        sa.Column("env_code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=256), nullable=False),
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
        sa.CheckConstraint(
            "length(trim(env_code)) > 0",
            name="ck_app_registry_environments_env_code_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_app_registry_environments_name_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(description)) > 0",
            name="ck_app_registry_environments_description_non_empty",
        ),
        sa.PrimaryKeyConstraint("env_code", name="pk_app_registry_environments"),
    )

    op.execute(
        """
        INSERT INTO app_registry_environments (
          env_code,
          name,
          description,
          sort_order,
          is_active
        )
        SELECT DISTINCT
          env_code,
          env_code,
          'Restored by downgrade from app registry runtime metadata',
          0,
          TRUE
        FROM (
          SELECT env_code FROM app_registry_endpoints
          UNION
          SELECT env_code FROM app_registry_databases
          UNION
          SELECT env_code FROM app_registry_gateway_bindings
          UNION
          SELECT env_code FROM app_registry_health_checks
          UNION
          SELECT env_code FROM app_registry_openapi_sources
        ) AS envs
        WHERE env_code IS NOT NULL
        ON CONFLICT (env_code) DO NOTHING
        """
    )

    op.create_table(
        "app_registry_components",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("component_code", sa.String(length=64), nullable=False),
        sa.Column("component_type", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("is_required", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
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
        sa.CheckConstraint(
            "length(trim(component_code)) > 0",
            name="ck_app_registry_components_component_code_non_empty",
        ),
        sa.CheckConstraint(
            "component_type IN ('api', 'web', 'worker', 'job', 'scheduler', 'proxy', 'gateway')",
            name="ck_app_registry_components_component_type_known",
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_app_registry_components_name_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(description)) > 0",
            name="ck_app_registry_components_description_non_empty",
        ),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_components_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_components"),
        sa.UniqueConstraint(
            "app_code",
            "component_code",
            name="uq_app_registry_components_app_component",
        ),
    )
    op.create_index(
        "ix_app_registry_components_app_code",
        "app_registry_components",
        ["app_code"],
    )

    op.add_column(
        "app_registry_endpoints",
        sa.Column("component_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_app_registry_endpoints_component_id_components",
        "app_registry_endpoints",
        "app_registry_components",
        ["component_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_foreign_key(
        "fk_app_registry_endpoints_env_code_environments",
        "app_registry_endpoints",
        "app_registry_environments",
        ["env_code"],
        ["env_code"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_app_registry_databases_env_code_environments",
        "app_registry_databases",
        "app_registry_environments",
        ["env_code"],
        ["env_code"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_app_registry_gateway_bindings_env_code_environments",
        "app_registry_gateway_bindings",
        "app_registry_environments",
        ["env_code"],
        ["env_code"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_app_registry_health_checks_env_code_environments",
        "app_registry_health_checks",
        "app_registry_environments",
        ["env_code"],
        ["env_code"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_app_registry_openapi_sources_env_code_environments",
        "app_registry_openapi_sources",
        "app_registry_environments",
        ["env_code"],
        ["env_code"],
        ondelete="CASCADE",
    )

    op.create_table(
        "app_registry_app_environments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("env_code", sa.String(length=32), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("notes", sa.String(length=512), nullable=True),
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
        sa.CheckConstraint(
            "length(trim(display_name)) > 0",
            name="ck_app_registry_app_environments_display_name_non_empty",
        ),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_app_environments_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["env_code"],
            ["app_registry_environments.env_code"],
            name="fk_app_registry_app_environments_env_code_environments",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_app_environments"),
        sa.UniqueConstraint(
            "app_code",
            "env_code",
            name="uq_app_registry_app_environments_app_env",
        ),
    )
    op.create_index(
        "ix_app_registry_app_environments_app_code",
        "app_registry_app_environments",
        ["app_code"],
    )
    op.create_index(
        "ix_app_registry_app_environments_env_code",
        "app_registry_app_environments",
        ["env_code"],
    )

    op.execute(
        """
        INSERT INTO app_registry_app_environments (
          app_code,
          env_code,
          display_name,
          is_default,
          is_active,
          notes
        )
        SELECT DISTINCT
          app_code,
          env_code,
          app_code || ':' || env_code,
          env_code = 'local',
          TRUE,
          'Restored by downgrade from app registry runtime metadata'
        FROM app_registry_endpoints
        ON CONFLICT (app_code, env_code) DO NOTHING
        """
    )

    op.create_table(
        "app_registry_repositories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("component_id", sa.Integer(), nullable=True),
        sa.Column("repo_type", sa.String(length=32), nullable=False),
        sa.Column("provider", sa.String(length=32), server_default="github", nullable=False),
        sa.Column("repo_owner", sa.String(length=128), nullable=False),
        sa.Column("repo_name", sa.String(length=128), nullable=False),
        sa.Column("default_branch", sa.String(length=64), server_default="main", nullable=False),
        sa.Column("local_path", sa.String(length=256), nullable=True),
        sa.Column("ci_workflow_name", sa.String(length=128), nullable=True),
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
        sa.CheckConstraint(
            "repo_type IN ('api', 'web', 'gateway', 'docs', 'infra', 'worker')",
            name="ck_app_registry_repositories_repo_type_known",
        ),
        sa.CheckConstraint(
            "length(trim(provider)) > 0",
            name="ck_app_registry_repositories_provider_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(repo_owner)) > 0",
            name="ck_app_registry_repositories_repo_owner_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(repo_name)) > 0",
            name="ck_app_registry_repositories_repo_name_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(default_branch)) > 0",
            name="ck_app_registry_repositories_default_branch_non_empty",
        ),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_repositories_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["component_id"],
            ["app_registry_components.id"],
            name="fk_app_registry_repositories_component_id_components",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_repositories"),
        sa.UniqueConstraint(
            "app_code",
            "repo_type",
            "repo_name",
            name="uq_app_registry_repositories_app_type_repo",
        ),
    )
    op.create_index(
        "ix_app_registry_repositories_app_code",
        "app_registry_repositories",
        ["app_code"],
    )
