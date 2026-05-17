from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AppRegistryEndpoint(Base):
    __tablename__ = "app_registry_endpoints"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    app_code: Mapped[str] = mapped_column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_endpoints_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    env_code: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    endpoint_type: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    method: Mapped[str | None] = mapped_column(sa.String(16), nullable=True)
    path: Mapped[str | None] = mapped_column(sa.String(256), nullable=True)
    url: Mapped[str] = mapped_column(sa.String(512), nullable=False)
    auth_required: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("false"),
    )
    timeout_ms: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="5000")
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("true"),
    )
    sort_order: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "app_code",
            "env_code",
            "endpoint_type",
            "name",
            name=sa.schema.conv("uq_app_registry_endpoints_app_env_type_name"),
        ),
        sa.CheckConstraint(
            "endpoint_type IN ('web', 'api', 'health', 'db_health', 'openapi', 'metrics', 'docs')",
            name=sa.schema.conv("ck_app_registry_endpoints_endpoint_type_known"),
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name=sa.schema.conv("ck_app_registry_endpoints_name_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(url)) > 0",
            name=sa.schema.conv("ck_app_registry_endpoints_url_non_empty"),
        ),
        sa.CheckConstraint(
            "timeout_ms > 0",
            name=sa.schema.conv("ck_app_registry_endpoints_timeout_positive"),
        ),
        sa.Index("ix_app_registry_endpoints_app_code", "app_code"),
        sa.Index("ix_app_registry_endpoints_env_type", "env_code", "endpoint_type"),
    )


class AppRegistryDatabase(Base):
    __tablename__ = "app_registry_databases"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    app_code: Mapped[str] = mapped_column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_databases_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    env_code: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    db_engine: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    db_host_label: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    db_port: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    db_name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    schema_name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    migration_tool: Mapped[str | None] = mapped_column(sa.String(64), nullable=True)
    migration_command: Mapped[str | None] = mapped_column(sa.String(256), nullable=True)
    health_endpoint_id: Mapped[int | None] = mapped_column(
        sa.Integer,
        sa.ForeignKey(
            "app_registry_endpoints.id",
            name="fk_app_registry_databases_health_endpoint_id_endpoints",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    secret_ref: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    access_policy: Mapped[str] = mapped_column(
        sa.String(64),
        nullable=False,
        server_default="health_endpoint_only",
    )
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("true"),
    )
    notes: Mapped[str | None] = mapped_column(sa.String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "app_code",
            "env_code",
            "db_name",
            name=sa.schema.conv("uq_app_registry_databases_app_env_db_name"),
        ),
        sa.CheckConstraint(
            "length(trim(db_engine)) > 0",
            name=sa.schema.conv("ck_app_registry_databases_db_engine_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(db_host_label)) > 0",
            name=sa.schema.conv("ck_app_registry_databases_db_host_label_non_empty"),
        ),
        sa.CheckConstraint(
            "db_port > 0",
            name=sa.schema.conv("ck_app_registry_databases_db_port_positive"),
        ),
        sa.CheckConstraint(
            "length(trim(db_name)) > 0",
            name=sa.schema.conv("ck_app_registry_databases_db_name_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(schema_name)) > 0",
            name=sa.schema.conv("ck_app_registry_databases_schema_name_non_empty"),
        ),
        sa.CheckConstraint(
            "access_policy IN ('metadata_only', 'health_endpoint_only')",
            name=sa.schema.conv("ck_app_registry_databases_access_policy_known"),
        ),
        sa.Index("ix_app_registry_databases_app_code", "app_code"),
        sa.Index("ix_app_registry_databases_env_code", "env_code"),
    )


class AppRegistryGatewayBinding(Base):
    __tablename__ = "app_registry_gateway_bindings"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    app_code: Mapped[str] = mapped_column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_gateway_bindings_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    env_code: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    web_path: Mapped[str] = mapped_column(sa.String(256), nullable=False)
    api_path: Mapped[str] = mapped_column(sa.String(256), nullable=False)
    web_upstream_url: Mapped[str | None] = mapped_column(sa.String(512), nullable=True)
    api_upstream_url: Mapped[str | None] = mapped_column(sa.String(512), nullable=True)
    rewrite_mode: Mapped[str] = mapped_column(
        sa.String(32),
        nullable=False,
        server_default="preserve_prefix",
    )
    is_published: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("false"),
    )
    published_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("true"),
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "app_code",
            "env_code",
            "web_path",
            "api_path",
            name=sa.schema.conv("uq_app_registry_gateway_bindings_app_env_paths"),
        ),
        sa.CheckConstraint(
            "left(web_path, 1) = '/'",
            name=sa.schema.conv("ck_app_registry_gateway_bindings_web_path_slash"),
        ),
        sa.CheckConstraint(
            "left(api_path, 1) = '/'",
            name=sa.schema.conv("ck_app_registry_gateway_bindings_api_path_slash"),
        ),
        sa.CheckConstraint(
            "rewrite_mode IN ('preserve_prefix', 'strip_prefix')",
            name=sa.schema.conv("ck_app_registry_gateway_bindings_rewrite_mode_known"),
        ),
        sa.Index("ix_app_registry_gateway_bindings_app_code", "app_code"),
        sa.Index("ix_app_registry_gateway_bindings_env_code", "env_code"),
    )


class AppRegistryDependency(Base):
    __tablename__ = "app_registry_dependencies"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    source_app_code: Mapped[str] = mapped_column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_dependencies_source_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    target_app_code: Mapped[str] = mapped_column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_dependencies_target_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    dependency_type: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    description: Mapped[str] = mapped_column(sa.String(512), nullable=False)
    is_required: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("true"),
    )
    status: Mapped[str] = mapped_column(sa.String(32), nullable=False, server_default="planned")
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("true"),
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "source_app_code",
            "target_app_code",
            "dependency_type",
            name=sa.schema.conv("uq_app_registry_dependencies_source_target_type"),
        ),
        sa.CheckConstraint(
            "dependency_type IN ('http_api', 'projection_feed', 'webhook', 'file_exchange')",
            name=sa.schema.conv("ck_app_registry_dependencies_dependency_type_known"),
        ),
        sa.CheckConstraint(
            "status IN ('planned', 'ready', 'deprecated')",
            name=sa.schema.conv("ck_app_registry_dependencies_status_known"),
        ),
        sa.CheckConstraint(
            "length(trim(description)) > 0",
            name=sa.schema.conv("ck_app_registry_dependencies_description_non_empty"),
        ),
        sa.Index("ix_app_registry_dependencies_source_app_code", "source_app_code"),
        sa.Index("ix_app_registry_dependencies_target_app_code", "target_app_code"),
    )


class AppRegistryServiceClient(Base):
    __tablename__ = "app_registry_service_clients"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    app_code: Mapped[str] = mapped_column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_service_clients_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    client_code: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    client_name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    auth_type: Mapped[str] = mapped_column(sa.String(32), nullable=False, server_default="none")
    secret_ref: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("false"),
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "app_code",
            "client_code",
            name=sa.schema.conv("uq_app_registry_service_clients_app_client"),
        ),
        sa.CheckConstraint(
            "auth_type IN ('none', 'static_token', 'client_credentials')",
            name=sa.schema.conv("ck_app_registry_service_clients_auth_type_known"),
        ),
        sa.CheckConstraint(
            "length(trim(client_code)) > 0",
            name=sa.schema.conv("ck_app_registry_service_clients_client_code_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(client_name)) > 0",
            name=sa.schema.conv("ck_app_registry_service_clients_client_name_non_empty"),
        ),
        sa.Index("ix_app_registry_service_clients_app_code", "app_code"),
    )


class AppRegistryServicePermission(Base):
    __tablename__ = "app_registry_service_permissions"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey(
            "app_registry_service_clients.id",
            name="fk_app_registry_service_permissions_client_id_clients",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    source_app_code: Mapped[str] = mapped_column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_service_permissions_source_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    target_app_code: Mapped[str] = mapped_column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_service_permissions_target_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    permission_code: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    description: Mapped[str] = mapped_column(sa.String(512), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("false"),
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "client_id",
            "permission_code",
            name=sa.schema.conv("uq_app_registry_service_permissions_client_permission"),
        ),
        sa.CheckConstraint(
            "length(trim(permission_code)) > 0",
            name=sa.schema.conv("ck_app_registry_service_permissions_permission_code_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(description)) > 0",
            name=sa.schema.conv("ck_app_registry_service_permissions_description_non_empty"),
        ),
        sa.Index("ix_app_registry_service_permissions_client_id", "client_id"),
        sa.Index("ix_app_registry_service_permissions_source_app_code", "source_app_code"),
        sa.Index("ix_app_registry_service_permissions_target_app_code", "target_app_code"),
    )


class AppRegistryHealthCheck(Base):
    __tablename__ = "app_registry_health_checks"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    app_code: Mapped[str] = mapped_column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_health_checks_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    env_code: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    endpoint_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey(
            "app_registry_endpoints.id",
            name="fk_app_registry_health_checks_endpoint_id_endpoints",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    check_type: Mapped[str] = mapped_column(
        sa.String(32),
        nullable=False,
        server_default="http_status",
    )
    expected_status: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        server_default="200",
    )
    expected_json_path: Mapped[str | None] = mapped_column(sa.String(256), nullable=True)
    expected_json_value: Mapped[str | None] = mapped_column(sa.String(256), nullable=True)
    timeout_ms: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="5000")
    interval_seconds: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        server_default="60",
    )
    severity: Mapped[str] = mapped_column(
        sa.String(32),
        nullable=False,
        server_default="critical",
    )
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("true"),
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "app_code",
            "env_code",
            "endpoint_id",
            "check_type",
            name=sa.schema.conv("uq_app_registry_health_checks_app_env_endpoint_type"),
        ),
        sa.CheckConstraint(
            "check_type IN ('http_status', 'json_value')",
            name=sa.schema.conv("ck_app_registry_health_checks_check_type_known"),
        ),
        sa.CheckConstraint(
            "expected_status > 0",
            name=sa.schema.conv("ck_app_registry_health_checks_expected_status_positive"),
        ),
        sa.CheckConstraint(
            "timeout_ms > 0",
            name=sa.schema.conv("ck_app_registry_health_checks_timeout_positive"),
        ),
        sa.CheckConstraint(
            "interval_seconds > 0",
            name=sa.schema.conv("ck_app_registry_health_checks_interval_positive"),
        ),
        sa.CheckConstraint(
            "severity IN ('info', 'warning', 'critical')",
            name=sa.schema.conv("ck_app_registry_health_checks_severity_known"),
        ),
        sa.Index("ix_app_registry_health_checks_app_code", "app_code"),
        sa.Index("ix_app_registry_health_checks_env_code", "env_code"),
        sa.Index("ix_app_registry_health_checks_endpoint_id", "endpoint_id"),
    )


class AppRegistryHealthCheckRun(Base):
    __tablename__ = "app_registry_health_check_runs"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    health_check_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey(
            "app_registry_health_checks.id",
            name="fk_app_registry_health_check_runs_health_check_id_checks",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    finished_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(sa.String(32), nullable=False, server_default="pending")
    http_status: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    message: Mapped[str | None] = mapped_column(sa.String(512), nullable=True)
    raw_excerpt: Mapped[str | None] = mapped_column(sa.String(2048), nullable=True)

    __table_args__ = (
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'success', 'failure', 'error', 'timeout')",
            name=sa.schema.conv("ck_app_registry_health_check_runs_status_known"),
        ),
        sa.CheckConstraint(
            "http_status IS NULL OR http_status > 0",
            name=sa.schema.conv("ck_app_registry_health_check_runs_http_status_positive"),
        ),
        sa.CheckConstraint(
            "latency_ms IS NULL OR latency_ms >= 0",
            name=sa.schema.conv("ck_app_registry_health_check_runs_latency_non_negative"),
        ),
        sa.Index("ix_app_registry_health_check_runs_health_check_id", "health_check_id"),
        sa.Index("ix_app_registry_health_check_runs_started_at", "started_at"),
        sa.Index("ix_app_registry_health_check_runs_status", "status"),
    )


class AppRegistryOpenApiSource(Base):
    __tablename__ = "app_registry_openapi_sources"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    app_code: Mapped[str] = mapped_column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_openapi_sources_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    env_code: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    endpoint_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey(
            "app_registry_endpoints.id",
            name="fk_app_registry_openapi_sources_endpoint_id_endpoints",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    openapi_url: Mapped[str] = mapped_column(sa.String(512), nullable=False)
    last_fetched_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    last_checksum: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    last_status: Mapped[str] = mapped_column(
        sa.String(32),
        nullable=False,
        server_default="unknown",
    )
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("true"),
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "app_code",
            "env_code",
            "endpoint_id",
            name=sa.schema.conv("uq_app_registry_openapi_sources_app_env_endpoint"),
        ),
        sa.CheckConstraint(
            "length(trim(openapi_url)) > 0",
            name=sa.schema.conv("ck_app_registry_openapi_sources_url_non_empty"),
        ),
        sa.CheckConstraint(
            "last_status IN ('unknown', 'success', 'failure')",
            name=sa.schema.conv("ck_app_registry_openapi_sources_last_status_known"),
        ),
        sa.Index("ix_app_registry_openapi_sources_app_code", "app_code"),
        sa.Index("ix_app_registry_openapi_sources_env_code", "env_code"),
        sa.Index("ix_app_registry_openapi_sources_endpoint_id", "endpoint_id"),
    )


__all__ = [
    "AppRegistryDatabase",
    "AppRegistryDependency",
    "AppRegistryEndpoint",
    "AppRegistryGatewayBinding",
    "AppRegistryHealthCheck",
    "AppRegistryHealthCheckRun",
    "AppRegistryOpenApiSource",
    "AppRegistryServiceClient",
    "AppRegistryServicePermission",
]
