# app/app_registry/models/app_registry_iam_projection.py
from __future__ import annotations

import sqlalchemy as sa

from app.db.base import Base


class AppRegistryIamSyncRun(Base):
    __tablename__ = "app_registry_iam_sync_runs"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    app_code = sa.Column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_reg_iam_sync_runs_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    source_base_url = sa.Column(sa.String(255), nullable=False)
    status = sa.Column(sa.String(32), nullable=False, server_default="running")
    started_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    finished_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    source_snapshot_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    fetched_count = sa.Column(sa.Integer, nullable=False, server_default="0")
    inserted_count = sa.Column(sa.Integer, nullable=False, server_default="0")
    updated_count = sa.Column(sa.Integer, nullable=False, server_default="0")
    deleted_count = sa.Column(sa.Integer, nullable=False, server_default="0")

    error_message = sa.Column(sa.Text, nullable=True)
    raw_excerpt = sa.Column(sa.Text, nullable=True)

    __table_args__ = (
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
        sa.Index("ix_app_reg_iam_sync_runs_app_code", "app_code"),
        sa.Index("ix_app_reg_iam_sync_runs_started_at", "started_at"),
        sa.Index("ix_app_reg_iam_sync_runs_status", "status"),
    )


class AppRegistryIamUserProjection(Base):
    __tablename__ = "app_registry_iam_user_projection"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    app_code = sa.Column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_reg_iam_user_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    source_user_id = sa.Column(sa.Integer, nullable=False)
    username = sa.Column(sa.String(128), nullable=False)
    is_active = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("true"))
    full_name = sa.Column(sa.String(255), nullable=True)
    phone = sa.Column(sa.String(64), nullable=True)
    email = sa.Column(sa.String(255), nullable=True)

    raw_payload = sa.Column(sa.JSON, nullable=True)
    last_sync_run_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey(
            "app_registry_iam_sync_runs.id",
            name="fk_app_reg_iam_user_sync_run",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    last_synced_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    __table_args__ = (
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
        sa.Index("ix_app_reg_iam_user_app_code", "app_code"),
        sa.Index("ix_app_reg_iam_user_username", "username"),
    )


class AppRegistryIamPermissionProjection(Base):
    __tablename__ = "app_registry_iam_permission_projection"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    app_code = sa.Column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_reg_iam_perm_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    source_permission_id = sa.Column(sa.Integer, nullable=False)
    permission_code = sa.Column(sa.String(255), nullable=False)

    raw_payload = sa.Column(sa.JSON, nullable=True)
    last_sync_run_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey(
            "app_registry_iam_sync_runs.id",
            name="fk_app_reg_iam_perm_sync_run",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    last_synced_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    __table_args__ = (
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
        sa.Index("ix_app_reg_iam_perm_app_code", "app_code"),
    )


class AppRegistryIamUserPermissionProjection(Base):
    __tablename__ = "app_registry_iam_user_permission_projection"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    app_code = sa.Column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_reg_iam_user_perm_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    source_user_id = sa.Column(sa.Integer, nullable=False)
    source_permission_id = sa.Column(sa.Integer, nullable=False)
    permission_code = sa.Column(sa.String(255), nullable=False)
    granted_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    raw_payload = sa.Column(sa.JSON, nullable=True)
    last_sync_run_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey(
            "app_registry_iam_sync_runs.id",
            name="fk_app_reg_iam_user_perm_sync_run",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    last_synced_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    __table_args__ = (
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
        sa.Index("ix_app_reg_iam_user_perm_app_code", "app_code"),
        sa.Index("ix_app_reg_iam_user_perm_user", "app_code", "source_user_id"),
    )


class AppRegistryIamPageProjection(Base):
    __tablename__ = "app_registry_iam_page_projection"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    app_code = sa.Column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_reg_iam_page_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    page_code = sa.Column(sa.String(128), nullable=False)
    page_name = sa.Column(sa.String(128), nullable=False)
    parent_page_code = sa.Column(sa.String(128), nullable=True)
    level = sa.Column(sa.Integer, nullable=False)
    domain_code = sa.Column(sa.String(64), nullable=True)

    show_in_topbar = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("false"))
    show_in_sidebar = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("true"))
    inherit_permissions = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("true"))

    read_permission_code = sa.Column(sa.String(255), nullable=True)
    write_permission_code = sa.Column(sa.String(255), nullable=True)
    sort_order = sa.Column(sa.Integer, nullable=True)
    is_active = sa.Column(sa.Boolean, nullable=True)

    raw_payload = sa.Column(sa.JSON, nullable=True)
    last_sync_run_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey(
            "app_registry_iam_sync_runs.id",
            name="fk_app_reg_iam_page_sync_run",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    last_synced_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    __table_args__ = (
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
        sa.Index("ix_app_reg_iam_page_app_code", "app_code"),
        sa.Index("ix_app_reg_iam_page_parent", "app_code", "parent_page_code"),
    )


class AppRegistryIamPageRoutePrefixProjection(Base):
    __tablename__ = "app_registry_iam_page_route_prefix_projection"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    app_code = sa.Column(
        sa.String(64),
        sa.ForeignKey(
            "app_registry_apps.code",
            name="fk_app_reg_iam_route_app_code_apps",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    page_code = sa.Column(sa.String(128), nullable=False)
    route_prefix = sa.Column(sa.String(255), nullable=False)
    sort_order = sa.Column(sa.Integer, nullable=True)
    is_active = sa.Column(sa.Boolean, nullable=True)

    raw_payload = sa.Column(sa.JSON, nullable=True)
    last_sync_run_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey(
            "app_registry_iam_sync_runs.id",
            name="fk_app_reg_iam_route_sync_run",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    last_synced_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    __table_args__ = (
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
        sa.Index("ix_app_reg_iam_route_app_code", "app_code"),
        sa.Index("ix_app_reg_iam_route_page", "app_code", "page_code"),
    )


__all__ = [
    "AppRegistryIamPageProjection",
    "AppRegistryIamPageRoutePrefixProjection",
    "AppRegistryIamPermissionProjection",
    "AppRegistryIamSyncRun",
    "AppRegistryIamUserPermissionProjection",
    "AppRegistryIamUserProjection",
]
