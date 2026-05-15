from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AppRegistryComponent(Base):
    __tablename__ = "app_registry_components"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    app_code: Mapped[str] = mapped_column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_components_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    component_code: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    component_type: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    description: Mapped[str] = mapped_column(sa.String(512), nullable=False)
    is_required: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("true"),
    )
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
            "component_code",
            name=sa.schema.conv("uq_app_registry_components_app_component"),
        ),
        sa.CheckConstraint(
            "length(trim(component_code)) > 0",
            name=sa.schema.conv("ck_app_registry_components_component_code_non_empty"),
        ),
        sa.CheckConstraint(
            "component_type IN ('api', 'web', 'worker', 'job', 'scheduler', 'proxy', 'gateway')",
            name=sa.schema.conv("ck_app_registry_components_component_type_known"),
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name=sa.schema.conv("ck_app_registry_components_name_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(description)) > 0",
            name=sa.schema.conv("ck_app_registry_components_description_non_empty"),
        ),
        sa.Index("ix_app_registry_components_app_code", "app_code"),
    )


class AppRegistryEnvironment(Base):
    __tablename__ = "app_registry_environments"

    env_code: Mapped[str] = mapped_column(sa.String(32), primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    description: Mapped[str] = mapped_column(sa.String(256), nullable=False)
    sort_order: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="0")
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
        sa.CheckConstraint(
            "length(trim(env_code)) > 0",
            name=sa.schema.conv("ck_app_registry_environments_env_code_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name=sa.schema.conv("ck_app_registry_environments_name_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(description)) > 0",
            name=sa.schema.conv("ck_app_registry_environments_description_non_empty"),
        ),
    )


class AppRegistryAppEnvironment(Base):
    __tablename__ = "app_registry_app_environments"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    app_code: Mapped[str] = mapped_column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_app_environments_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    env_code: Mapped[str] = mapped_column(
        sa.String(32),
        sa.ForeignKey(
            "app_registry_environments.env_code",
            name="fk_app_registry_app_environments_env_code_environments",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    is_default: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("false"),
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
            name=sa.schema.conv("uq_app_registry_app_environments_app_env"),
        ),
        sa.CheckConstraint(
            "length(trim(display_name)) > 0",
            name=sa.schema.conv("ck_app_registry_app_environments_display_name_non_empty"),
        ),
        sa.Index("ix_app_registry_app_environments_app_code", "app_code"),
        sa.Index("ix_app_registry_app_environments_env_code", "env_code"),
    )


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
    component_id: Mapped[int | None] = mapped_column(
        sa.Integer,
        sa.ForeignKey(
            "app_registry_components.id",
            name="fk_app_registry_endpoints_component_id_components",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    env_code: Mapped[str] = mapped_column(
        sa.String(32),
        sa.ForeignKey(
            "app_registry_environments.env_code",
            name="fk_app_registry_endpoints_env_code_environments",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
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
    env_code: Mapped[str] = mapped_column(
        sa.String(32),
        sa.ForeignKey(
            "app_registry_environments.env_code",
            name="fk_app_registry_databases_env_code_environments",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
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


class AppRegistryRepositoryMeta(Base):
    __tablename__ = "app_registry_repositories"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    app_code: Mapped[str] = mapped_column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_registry_repositories_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    component_id: Mapped[int | None] = mapped_column(
        sa.Integer,
        sa.ForeignKey(
            "app_registry_components.id",
            name="fk_app_registry_repositories_component_id_components",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    repo_type: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    provider: Mapped[str] = mapped_column(sa.String(32), nullable=False, server_default="github")
    repo_owner: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    repo_name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    default_branch: Mapped[str] = mapped_column(
        sa.String(64),
        nullable=False,
        server_default="main",
    )
    local_path: Mapped[str | None] = mapped_column(sa.String(256), nullable=True)
    ci_workflow_name: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
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
            "repo_type",
            "repo_name",
            name=sa.schema.conv("uq_app_registry_repositories_app_type_repo"),
        ),
        sa.CheckConstraint(
            "repo_type IN ('api', 'web', 'gateway', 'docs', 'infra', 'worker')",
            name=sa.schema.conv("ck_app_registry_repositories_repo_type_known"),
        ),
        sa.CheckConstraint(
            "length(trim(provider)) > 0",
            name=sa.schema.conv("ck_app_registry_repositories_provider_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(repo_owner)) > 0",
            name=sa.schema.conv("ck_app_registry_repositories_repo_owner_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(repo_name)) > 0",
            name=sa.schema.conv("ck_app_registry_repositories_repo_name_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(default_branch)) > 0",
            name=sa.schema.conv("ck_app_registry_repositories_default_branch_non_empty"),
        ),
        sa.Index("ix_app_registry_repositories_app_code", "app_code"),
    )


__all__ = [
    "AppRegistryAppEnvironment",
    "AppRegistryComponent",
    "AppRegistryDatabase",
    "AppRegistryEndpoint",
    "AppRegistryEnvironment",
    "AppRegistryRepositoryMeta",
]
