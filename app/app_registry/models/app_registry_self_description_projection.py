# app/app_registry/models/app_registry_self_description_projection.py
from __future__ import annotations

import sqlalchemy as sa

from app.db.base import Base


class AppRegistrySelfDescriptionSyncRun(Base):
    __tablename__ = "app_registry_self_description_sync_runs"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    app_code = sa.Column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_self_desc_sync_runs_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    sync_type = sa.Column(sa.String(32), nullable=False)
    source_base_url = sa.Column(sa.String(255), nullable=False)
    status = sa.Column(sa.String(32), nullable=False, server_default="running")

    started_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    finished_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    fetched_count = sa.Column(sa.Integer, nullable=False, server_default="0")
    inserted_count = sa.Column(sa.Integer, nullable=False, server_default="0")
    updated_count = sa.Column(sa.Integer, nullable=False, server_default="0")
    deleted_count = sa.Column(sa.Integer, nullable=False, server_default="0")

    error_message = sa.Column(sa.Text, nullable=True)
    raw_excerpt = sa.Column(sa.Text, nullable=True)

    __table_args__ = (
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
        sa.Index("ix_app_registry_self_desc_sync_runs_app_code", "app_code"),
        sa.Index("ix_app_registry_self_desc_sync_runs_status", "status"),
        sa.Index("ix_app_registry_self_desc_sync_runs_started_at", "started_at"),
    )


class AppRegistryAppManifestSnapshot(Base):
    __tablename__ = "app_registry_app_manifest_snapshots"

    app_code = sa.Column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_app_manifest_snapshots_app_code_apps",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    app_name = sa.Column(sa.String(128), nullable=False)
    app_type = sa.Column(sa.String(64), nullable=False)
    status = sa.Column(sa.String(32), nullable=False)
    description = sa.Column(sa.Text, nullable=False)

    default_web_path = sa.Column(sa.String(255), nullable=False)
    default_api_path = sa.Column(sa.String(255), nullable=False)
    local_web_url = sa.Column(sa.String(255), nullable=False)
    local_api_url = sa.Column(sa.String(255), nullable=False)

    health_url = sa.Column(sa.String(255), nullable=False)
    db_health_url = sa.Column(sa.String(255), nullable=True)
    openapi_url = sa.Column(sa.String(255), nullable=False)
    page_catalog_url = sa.Column(sa.String(255), nullable=False)
    service_capabilities_url = sa.Column(sa.String(255), nullable=False)
    service_dependencies_url = sa.Column(sa.String(255), nullable=False)

    version = sa.Column(sa.String(64), nullable=False)
    build_environment = sa.Column(sa.String(64), nullable=True)
    build_git_sha = sa.Column(sa.String(128), nullable=True)
    build_time = sa.Column(sa.String(128), nullable=True)

    raw_manifest = sa.Column(sa.JSON, nullable=True)
    last_sync_run_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey(
            "app_registry_self_description_sync_runs.id",
            name="fk_app_registry_app_manifest_snapshots_sync_run",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    last_synced_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
        onupdate=sa.text("now()"),
    )

    __table_args__ = (
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
        sa.Index("ix_app_registry_app_manifest_snapshots_last_sync_run_id", "last_sync_run_id"),
    )


class AppRegistryPageCatalogPage(Base):
    __tablename__ = "app_registry_page_catalog_pages"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    app_code = sa.Column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_page_catalog_pages_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    page_code = sa.Column(sa.String(128), nullable=False)
    page_name = sa.Column(sa.String(128), nullable=False)
    route_path = sa.Column(sa.String(255), nullable=True)
    parent_page_code = sa.Column(sa.String(128), nullable=True)
    level = sa.Column(sa.Integer, nullable=False)
    read_permission_code = sa.Column(sa.String(255), nullable=True)
    write_permission_code = sa.Column(sa.String(255), nullable=True)
    is_active = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("true"))
    sort_order = sa.Column(sa.Integer, nullable=False, server_default="0")
    source_updated_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    raw_payload = sa.Column(sa.JSON, nullable=True)
    last_sync_run_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey(
            "app_registry_self_description_sync_runs.id",
            name="fk_app_registry_page_catalog_pages_sync_run",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    last_synced_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        sa.UniqueConstraint(
            "app_code",
            "page_code",
            name="uq_app_registry_page_catalog_pages_app_page",
        ),
        sa.CheckConstraint(
            "level IN (1, 2, 3)",
            name="ck_app_registry_page_catalog_pages_level",
        ),
        sa.CheckConstraint(
            "btrim(page_code) <> ''",
            name="ck_app_registry_page_catalog_pages_code_non_empty",
        ),
        sa.CheckConstraint(
            "btrim(page_name) <> ''",
            name="ck_app_registry_page_catalog_pages_name_non_empty",
        ),
        sa.Index("ix_app_registry_page_catalog_pages_app_code", "app_code"),
        sa.Index(
            "ix_app_registry_page_catalog_pages_parent",
            "app_code",
            "parent_page_code",
        ),
        sa.Index("ix_app_registry_page_catalog_pages_sync_run", "last_sync_run_id"),
    )


class AppRegistryServiceCapabilityCatalog(Base):
    __tablename__ = "app_registry_service_capability_catalog"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    app_code = sa.Column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_service_capability_catalog_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    capability_code = sa.Column(sa.String(128), nullable=False)
    capability_name = sa.Column(sa.String(128), nullable=False)
    resource_code = sa.Column(sa.String(64), nullable=False)
    permission_code = sa.Column(sa.String(128), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    is_active = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("true"))
    source_updated_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    raw_payload = sa.Column(sa.JSON, nullable=True)
    last_sync_run_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey(
            "app_registry_self_description_sync_runs.id",
            name="fk_app_registry_service_capability_catalog_sync_run",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    last_synced_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    __table_args__ = (
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
        sa.Index("ix_app_registry_service_capability_catalog_app_code", "app_code"),
        sa.Index(
            "ix_app_registry_service_capability_catalog_capability_code",
            "capability_code",
        ),
        sa.Index(
            "ix_app_registry_service_capability_catalog_sync_run",
            "last_sync_run_id",
        ),
    )


class AppRegistryServiceCapabilityRoute(Base):
    __tablename__ = "app_registry_service_capability_routes"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    app_code = sa.Column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_service_capability_routes_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    capability_code = sa.Column(sa.String(128), nullable=False)
    http_method = sa.Column(sa.String(16), nullable=False)
    path = sa.Column(sa.String(255), nullable=False)
    route_name = sa.Column(sa.String(128), nullable=False)
    auth_required = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("true"))
    is_active = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("true"))
    source_created_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    raw_payload = sa.Column(sa.JSON, nullable=True)
    last_sync_run_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey(
            "app_registry_self_description_sync_runs.id",
            name="fk_app_registry_service_capability_routes_sync_run",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    last_synced_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    __table_args__ = (
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
        sa.Index(
            "ix_app_registry_service_capability_routes_app_capability",
            "app_code",
            "capability_code",
        ),
        sa.Index(
            "ix_app_registry_service_capability_routes_sync_run",
            "last_sync_run_id",
        ),
    )


class AppRegistryServiceDependencyCatalog(Base):
    __tablename__ = "app_registry_service_dependency_catalog"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    source_app_code = sa.Column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_service_dependency_catalog_source_app_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    dependency_code = sa.Column(sa.String(128), nullable=False)
    dependency_name = sa.Column(sa.String(128), nullable=False)
    target_app_code = sa.Column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_service_dependency_catalog_target_app_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    target_capability_code = sa.Column(sa.String(128), nullable=False)
    required_permission_code = sa.Column(sa.String(128), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    is_required = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("true"))
    is_active = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("true"))
    required_config_keys = sa.Column(sa.JSON, nullable=False, server_default=sa.text("'[]'::json"))
    source_modules = sa.Column(sa.JSON, nullable=False, server_default=sa.text("'[]'::json"))

    raw_payload = sa.Column(sa.JSON, nullable=True)
    last_sync_run_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey(
            "app_registry_self_description_sync_runs.id",
            name="fk_app_registry_service_dependency_catalog_sync_run",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    last_synced_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    __table_args__ = (
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
        sa.Index(
            "ix_app_registry_service_dependency_catalog_source_app",
            "source_app_code",
        ),
        sa.Index(
            "ix_app_registry_service_dependency_catalog_target_app",
            "target_app_code",
        ),
        sa.Index(
            "ix_app_registry_service_dependency_catalog_target_capability",
            "target_app_code",
            "target_capability_code",
        ),
        sa.Index(
            "ix_app_registry_service_dependency_catalog_sync_run",
            "last_sync_run_id",
        ),
    )


class AppRegistryServiceDependencyEndpoint(Base):
    __tablename__ = "app_registry_service_dependency_endpoints"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    source_app_code = sa.Column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_service_dependency_endpoints_source_app_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    dependency_code = sa.Column(sa.String(128), nullable=False)
    http_method = sa.Column(sa.String(16), nullable=False)
    path = sa.Column(sa.String(255), nullable=False)
    purpose = sa.Column(sa.String(255), nullable=True)

    raw_payload = sa.Column(sa.JSON, nullable=True)
    last_sync_run_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey(
            "app_registry_self_description_sync_runs.id",
            name="fk_app_registry_service_dependency_endpoints_sync_run",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    last_synced_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    __table_args__ = (
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
        sa.Index(
            "ix_app_registry_service_dependency_endpoints_source_dependency",
            "source_app_code",
            "dependency_code",
        ),
        sa.Index(
            "ix_app_registry_service_dependency_endpoints_sync_run",
            "last_sync_run_id",
        ),
    )


__all__ = [
    "AppRegistryAppManifestSnapshot",
    "AppRegistryPageCatalogPage",
    "AppRegistrySelfDescriptionSyncRun",
    "AppRegistryServiceCapabilityCatalog",
    "AppRegistryServiceCapabilityRoute",
    "AppRegistryServiceDependencyCatalog",
    "AppRegistryServiceDependencyEndpoint",
]
