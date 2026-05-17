"""app_registry_self_description_projections

Revision ID: 0013_app_registry_self_desc
Revises: 0012_app_meta_retire
Create Date: 2026-05-17
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0013_app_registry_self_desc"
down_revision: str | Sequence[str] | None = "0012_app_meta_retire"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "app_registry_self_description_sync_runs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("sync_type", sa.String(length=32), nullable=False),
        sa.Column("source_base_url", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="running", nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fetched_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("inserted_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("updated_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("deleted_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("raw_excerpt", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_self_desc_sync_runs_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_self_description_sync_runs"),
        sa.CheckConstraint(
            "sync_type IN ("
            "'all', "
            "'app_manifest', "
            "'page_catalog', "
            "'service_capabilities', "
            "'service_dependencies'"
            ")",
            name="ck_app_registry_self_desc_sync_runs_sync_type_known",
        ),
        sa.CheckConstraint(
            "status IN ('running', 'success', 'failure')",
            name="ck_app_registry_self_desc_sync_runs_status_known",
        ),
        sa.CheckConstraint(
            "fetched_count >= 0 "
            "AND inserted_count >= 0 "
            "AND updated_count >= 0 "
            "AND deleted_count >= 0",
            name="ck_app_registry_self_desc_sync_runs_counts_non_negative",
        ),
    )
    op.create_index(
        "ix_app_registry_self_desc_sync_runs_app_code",
        "app_registry_self_description_sync_runs",
        ["app_code"],
    )
    op.create_index(
        "ix_app_registry_self_desc_sync_runs_status",
        "app_registry_self_description_sync_runs",
        ["status"],
    )
    op.create_index(
        "ix_app_registry_self_desc_sync_runs_started_at",
        "app_registry_self_description_sync_runs",
        ["started_at"],
    )

    op.create_table(
        "app_registry_app_manifest_snapshots",
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("app_name", sa.String(length=128), nullable=False),
        sa.Column("app_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("default_web_path", sa.String(length=255), nullable=False),
        sa.Column("default_api_path", sa.String(length=255), nullable=False),
        sa.Column("local_web_url", sa.String(length=255), nullable=False),
        sa.Column("local_api_url", sa.String(length=255), nullable=False),
        sa.Column("health_url", sa.String(length=255), nullable=False),
        sa.Column("db_health_url", sa.String(length=255), nullable=True),
        sa.Column("openapi_url", sa.String(length=255), nullable=False),
        sa.Column("page_catalog_url", sa.String(length=255), nullable=False),
        sa.Column("service_capabilities_url", sa.String(length=255), nullable=False),
        sa.Column("service_dependencies_url", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("build_environment", sa.String(length=64), nullable=True),
        sa.Column("build_git_sha", sa.String(length=128), nullable=True),
        sa.Column("build_time", sa.String(length=128), nullable=True),
        sa.Column("raw_manifest", sa.JSON(), nullable=True),
        sa.Column("last_sync_run_id", sa.BigInteger(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_app_manifest_snapshots_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["last_sync_run_id"],
            ["app_registry_self_description_sync_runs.id"],
            name="fk_app_registry_app_manifest_snapshots_sync_run",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("app_code", name="pk_app_registry_app_manifest_snapshots"),
        sa.CheckConstraint(
            "btrim(app_name) <> ''",
            name="ck_app_registry_app_manifest_snapshots_app_name_non_empty",
        ),
        sa.CheckConstraint(
            "default_web_path LIKE '/%'",
            name="ck_app_registry_app_manifest_snapshots_web_path_slash",
        ),
        sa.CheckConstraint(
            "default_api_path LIKE '/%'",
            name="ck_app_registry_app_manifest_snapshots_api_path_slash",
        ),
    )
    op.create_index(
        "ix_app_registry_app_manifest_snapshots_last_sync_run_id",
        "app_registry_app_manifest_snapshots",
        ["last_sync_run_id"],
    )

    op.create_table(
        "app_registry_page_catalog_pages",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("page_code", sa.String(length=128), nullable=False),
        sa.Column("page_name", sa.String(length=128), nullable=False),
        sa.Column("route_path", sa.String(length=255), nullable=True),
        sa.Column("parent_page_code", sa.String(length=128), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("read_permission_code", sa.String(length=255), nullable=True),
        sa.Column("write_permission_code", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("last_sync_run_id", sa.BigInteger(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_page_catalog_pages_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["last_sync_run_id"],
            ["app_registry_self_description_sync_runs.id"],
            name="fk_app_registry_page_catalog_pages_sync_run",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_page_catalog_pages"),
        sa.UniqueConstraint(
            "app_code",
            "page_code",
            name="uq_app_registry_page_catalog_pages_app_page",
        ),
        sa.CheckConstraint("level IN (1, 2, 3)", name="ck_app_registry_page_catalog_pages_level"),
        sa.CheckConstraint(
            "btrim(page_code) <> ''",
            name="ck_app_registry_page_catalog_pages_code_non_empty",
        ),
        sa.CheckConstraint(
            "btrim(page_name) <> ''",
            name="ck_app_registry_page_catalog_pages_name_non_empty",
        ),
    )
    op.create_index(
        "ix_app_registry_page_catalog_pages_app_code",
        "app_registry_page_catalog_pages",
        ["app_code"],
    )
    op.create_index(
        "ix_app_registry_page_catalog_pages_parent",
        "app_registry_page_catalog_pages",
        ["app_code", "parent_page_code"],
    )
    op.create_index(
        "ix_app_registry_page_catalog_pages_sync_run",
        "app_registry_page_catalog_pages",
        ["last_sync_run_id"],
    )

    op.create_table(
        "app_registry_service_capability_catalog",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("capability_code", sa.String(length=128), nullable=False),
        sa.Column("capability_name", sa.String(length=128), nullable=False),
        sa.Column("resource_code", sa.String(length=64), nullable=False),
        sa.Column("permission_code", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("last_sync_run_id", sa.BigInteger(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_service_capability_catalog_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["last_sync_run_id"],
            ["app_registry_self_description_sync_runs.id"],
            name="fk_app_registry_service_capability_catalog_sync_run",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_service_capability_catalog"),
        sa.UniqueConstraint(
            "app_code",
            "capability_code",
            name="uq_app_registry_service_capability_catalog_app_capability",
        ),
        sa.CheckConstraint(
            "btrim(capability_code) <> ''",
            name="ck_app_registry_service_capability_catalog_code_non_empty",
        ),
        sa.CheckConstraint(
            "btrim(permission_code) <> ''",
            name="ck_app_registry_service_capability_catalog_permission_non_empty",
        ),
    )
    op.create_index(
        "ix_app_registry_service_capability_catalog_app_code",
        "app_registry_service_capability_catalog",
        ["app_code"],
    )
    op.create_index(
        "ix_app_registry_service_capability_catalog_capability_code",
        "app_registry_service_capability_catalog",
        ["capability_code"],
    )
    op.create_index(
        "ix_app_registry_service_capability_catalog_sync_run",
        "app_registry_service_capability_catalog",
        ["last_sync_run_id"],
    )

    op.create_table(
        "app_registry_service_capability_routes",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("capability_code", sa.String(length=128), nullable=False),
        sa.Column("http_method", sa.String(length=16), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("route_name", sa.String(length=128), nullable=False),
        sa.Column("auth_required", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("source_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("last_sync_run_id", sa.BigInteger(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_service_capability_routes_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["last_sync_run_id"],
            ["app_registry_self_description_sync_runs.id"],
            name="fk_app_registry_service_capability_routes_sync_run",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_service_capability_routes"),
        sa.UniqueConstraint(
            "app_code",
            "capability_code",
            "http_method",
            "path",
            name="uq_app_registry_service_capability_routes_identity",
        ),
        sa.CheckConstraint(
            "btrim(capability_code) <> ''",
            name="ck_app_registry_service_capability_routes_capability_non_empty",
        ),
        sa.CheckConstraint(
            "btrim(path) <> ''",
            name="ck_app_registry_service_capability_routes_path_non_empty",
        ),
    )
    op.create_index(
        "ix_app_registry_service_capability_routes_app_capability",
        "app_registry_service_capability_routes",
        ["app_code", "capability_code"],
    )
    op.create_index(
        "ix_app_registry_service_capability_routes_sync_run",
        "app_registry_service_capability_routes",
        ["last_sync_run_id"],
    )

    op.create_table(
        "app_registry_service_dependency_catalog",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("source_app_code", sa.String(length=64), nullable=False),
        sa.Column("dependency_code", sa.String(length=128), nullable=False),
        sa.Column("dependency_name", sa.String(length=128), nullable=False),
        sa.Column("target_app_code", sa.String(length=64), nullable=False),
        sa.Column("target_capability_code", sa.String(length=128), nullable=False),
        sa.Column("required_permission_code", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_required", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "required_config_keys",
            sa.JSON(),
            server_default=sa.text("'[]'::json"),
            nullable=False,
        ),
        sa.Column(
            "source_modules",
            sa.JSON(),
            server_default=sa.text("'[]'::json"),
            nullable=False,
        ),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("last_sync_run_id", sa.BigInteger(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["source_app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_service_dependency_catalog_source_app_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_service_dependency_catalog_target_app_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["last_sync_run_id"],
            ["app_registry_self_description_sync_runs.id"],
            name="fk_app_registry_service_dependency_catalog_sync_run",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_service_dependency_catalog"),
        sa.UniqueConstraint(
            "source_app_code",
            "dependency_code",
            name="uq_app_registry_service_dependency_catalog_source_dependency",
        ),
        sa.CheckConstraint(
            "btrim(dependency_code) <> ''",
            name="ck_app_registry_service_dependency_catalog_code_non_empty",
        ),
        sa.CheckConstraint(
            "btrim(target_capability_code) <> ''",
            name="ck_app_registry_service_dependency_catalog_target_cap_non_empty",
        ),
    )
    op.create_index(
        "ix_app_registry_service_dependency_catalog_source_app",
        "app_registry_service_dependency_catalog",
        ["source_app_code"],
    )
    op.create_index(
        "ix_app_registry_service_dependency_catalog_target_app",
        "app_registry_service_dependency_catalog",
        ["target_app_code"],
    )
    op.create_index(
        "ix_app_registry_service_dependency_catalog_target_capability",
        "app_registry_service_dependency_catalog",
        ["target_app_code", "target_capability_code"],
    )
    op.create_index(
        "ix_app_registry_service_dependency_catalog_sync_run",
        "app_registry_service_dependency_catalog",
        ["last_sync_run_id"],
    )

    op.create_table(
        "app_registry_service_dependency_endpoints",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("source_app_code", sa.String(length=64), nullable=False),
        sa.Column("dependency_code", sa.String(length=128), nullable=False),
        sa.Column("http_method", sa.String(length=16), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("purpose", sa.String(length=255), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("last_sync_run_id", sa.BigInteger(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["source_app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_service_dependency_endpoints_source_app_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["last_sync_run_id"],
            ["app_registry_self_description_sync_runs.id"],
            name="fk_app_registry_service_dependency_endpoints_sync_run",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_service_dependency_endpoints"),
        sa.UniqueConstraint(
            "source_app_code",
            "dependency_code",
            "http_method",
            "path",
            name="uq_app_registry_service_dependency_endpoints_identity",
        ),
        sa.CheckConstraint(
            "btrim(dependency_code) <> ''",
            name="ck_app_registry_service_dependency_endpoints_code_non_empty",
        ),
        sa.CheckConstraint(
            "btrim(path) <> ''",
            name="ck_app_registry_service_dependency_endpoints_path_non_empty",
        ),
    )
    op.create_index(
        "ix_app_registry_service_dependency_endpoints_source_dependency",
        "app_registry_service_dependency_endpoints",
        ["source_app_code", "dependency_code"],
    )
    op.create_index(
        "ix_app_registry_service_dependency_endpoints_sync_run",
        "app_registry_service_dependency_endpoints",
        ["last_sync_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_app_registry_service_dependency_endpoints_sync_run",
        table_name="app_registry_service_dependency_endpoints",
    )
    op.drop_index(
        "ix_app_registry_service_dependency_endpoints_source_dependency",
        table_name="app_registry_service_dependency_endpoints",
    )
    op.drop_table("app_registry_service_dependency_endpoints")

    op.drop_index(
        "ix_app_registry_service_dependency_catalog_sync_run",
        table_name="app_registry_service_dependency_catalog",
    )
    op.drop_index(
        "ix_app_registry_service_dependency_catalog_target_capability",
        table_name="app_registry_service_dependency_catalog",
    )
    op.drop_index(
        "ix_app_registry_service_dependency_catalog_target_app",
        table_name="app_registry_service_dependency_catalog",
    )
    op.drop_index(
        "ix_app_registry_service_dependency_catalog_source_app",
        table_name="app_registry_service_dependency_catalog",
    )
    op.drop_table("app_registry_service_dependency_catalog")

    op.drop_index(
        "ix_app_registry_service_capability_routes_sync_run",
        table_name="app_registry_service_capability_routes",
    )
    op.drop_index(
        "ix_app_registry_service_capability_routes_app_capability",
        table_name="app_registry_service_capability_routes",
    )
    op.drop_table("app_registry_service_capability_routes")

    op.drop_index(
        "ix_app_registry_service_capability_catalog_sync_run",
        table_name="app_registry_service_capability_catalog",
    )
    op.drop_index(
        "ix_app_registry_service_capability_catalog_capability_code",
        table_name="app_registry_service_capability_catalog",
    )
    op.drop_index(
        "ix_app_registry_service_capability_catalog_app_code",
        table_name="app_registry_service_capability_catalog",
    )
    op.drop_table("app_registry_service_capability_catalog")

    op.drop_index(
        "ix_app_registry_page_catalog_pages_sync_run",
        table_name="app_registry_page_catalog_pages",
    )
    op.drop_index(
        "ix_app_registry_page_catalog_pages_parent",
        table_name="app_registry_page_catalog_pages",
    )
    op.drop_index(
        "ix_app_registry_page_catalog_pages_app_code",
        table_name="app_registry_page_catalog_pages",
    )
    op.drop_table("app_registry_page_catalog_pages")

    op.drop_index(
        "ix_app_registry_app_manifest_snapshots_last_sync_run_id",
        table_name="app_registry_app_manifest_snapshots",
    )
    op.drop_table("app_registry_app_manifest_snapshots")

    op.drop_index(
        "ix_app_registry_self_desc_sync_runs_started_at",
        table_name="app_registry_self_description_sync_runs",
    )
    op.drop_index(
        "ix_app_registry_self_desc_sync_runs_status",
        table_name="app_registry_self_description_sync_runs",
    )
    op.drop_index(
        "ix_app_registry_self_desc_sync_runs_app_code",
        table_name="app_registry_self_description_sync_runs",
    )
    op.drop_table("app_registry_self_description_sync_runs")
