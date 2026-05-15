# ruff: noqa: E501
"""app_registry_runtime_governance

Revision ID: 0009_app_registry_ops
Revises: 0008_app_registry_auth
Create Date: 2026-05-16 23:30:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0009_app_registry_ops"
down_revision: str | Sequence[str] | None = "0008_app_registry_auth"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "app_registry_health_checks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("env_code", sa.String(length=32), nullable=False),
        sa.Column("endpoint_id", sa.Integer(), nullable=False),
        sa.Column("check_type", sa.String(length=32), server_default="http_status", nullable=False),
        sa.Column("expected_status", sa.Integer(), server_default="200", nullable=False),
        sa.Column("expected_json_path", sa.String(length=256), nullable=True),
        sa.Column("expected_json_value", sa.String(length=256), nullable=True),
        sa.Column("timeout_ms", sa.Integer(), server_default="5000", nullable=False),
        sa.Column("interval_seconds", sa.Integer(), server_default="60", nullable=False),
        sa.Column("severity", sa.String(length=32), server_default="critical", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "check_type IN ('http_status', 'json_value')",
            name="ck_app_registry_health_checks_check_type_known",
        ),
        sa.CheckConstraint(
            "expected_status > 0",
            name="ck_app_registry_health_checks_expected_status_positive",
        ),
        sa.CheckConstraint(
            "timeout_ms > 0",
            name="ck_app_registry_health_checks_timeout_positive",
        ),
        sa.CheckConstraint(
            "interval_seconds > 0",
            name="ck_app_registry_health_checks_interval_positive",
        ),
        sa.CheckConstraint(
            "severity IN ('info', 'warning', 'critical')",
            name="ck_app_registry_health_checks_severity_known",
        ),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_health_checks_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["env_code"],
            ["app_registry_environments.env_code"],
            name="fk_app_registry_health_checks_env_code_environments",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["endpoint_id"],
            ["app_registry_endpoints.id"],
            name="fk_app_registry_health_checks_endpoint_id_endpoints",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_health_checks"),
        sa.UniqueConstraint(
            "app_code",
            "env_code",
            "endpoint_id",
            "check_type",
            name="uq_app_registry_health_checks_app_env_endpoint_type",
        ),
    )
    op.create_index(
        "ix_app_registry_health_checks_app_code",
        "app_registry_health_checks",
        ["app_code"],
    )
    op.create_index(
        "ix_app_registry_health_checks_env_code",
        "app_registry_health_checks",
        ["env_code"],
    )
    op.create_index(
        "ix_app_registry_health_checks_endpoint_id",
        "app_registry_health_checks",
        ["endpoint_id"],
    )

    op.create_table(
        "app_registry_health_check_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("health_check_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("message", sa.String(length=512), nullable=True),
        sa.Column("raw_excerpt", sa.String(length=2048), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'success', 'failure', 'error', 'timeout')",
            name="ck_app_registry_health_check_runs_status_known",
        ),
        sa.CheckConstraint(
            "http_status IS NULL OR http_status > 0",
            name="ck_app_registry_health_check_runs_http_status_positive",
        ),
        sa.CheckConstraint(
            "latency_ms IS NULL OR latency_ms >= 0",
            name="ck_app_registry_health_check_runs_latency_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["health_check_id"],
            ["app_registry_health_checks.id"],
            name="fk_app_registry_health_check_runs_health_check_id_checks",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_health_check_runs"),
    )
    op.create_index(
        "ix_app_registry_health_check_runs_health_check_id",
        "app_registry_health_check_runs",
        ["health_check_id"],
    )
    op.create_index(
        "ix_app_registry_health_check_runs_started_at",
        "app_registry_health_check_runs",
        ["started_at"],
    )
    op.create_index(
        "ix_app_registry_health_check_runs_status",
        "app_registry_health_check_runs",
        ["status"],
    )

    op.create_table(
        "app_registry_openapi_sources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("env_code", sa.String(length=32), nullable=False),
        sa.Column("endpoint_id", sa.Integer(), nullable=False),
        sa.Column("openapi_url", sa.String(length=512), nullable=False),
        sa.Column("last_fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_checksum", sa.String(length=128), nullable=True),
        sa.Column("last_status", sa.String(length=32), server_default="unknown", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "length(trim(openapi_url)) > 0",
            name="ck_app_registry_openapi_sources_url_non_empty",
        ),
        sa.CheckConstraint(
            "last_status IN ('unknown', 'success', 'failure')",
            name="ck_app_registry_openapi_sources_last_status_known",
        ),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_openapi_sources_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["env_code"],
            ["app_registry_environments.env_code"],
            name="fk_app_registry_openapi_sources_env_code_environments",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["endpoint_id"],
            ["app_registry_endpoints.id"],
            name="fk_app_registry_openapi_sources_endpoint_id_endpoints",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_openapi_sources"),
        sa.UniqueConstraint(
            "app_code",
            "env_code",
            "endpoint_id",
            name="uq_app_registry_openapi_sources_app_env_endpoint",
        ),
    )
    op.create_index(
        "ix_app_registry_openapi_sources_app_code",
        "app_registry_openapi_sources",
        ["app_code"],
    )
    op.create_index(
        "ix_app_registry_openapi_sources_env_code",
        "app_registry_openapi_sources",
        ["env_code"],
    )
    op.create_index(
        "ix_app_registry_openapi_sources_endpoint_id",
        "app_registry_openapi_sources",
        ["endpoint_id"],
    )

    _seed_runtime_governance_metadata()


def _seed_runtime_governance_metadata() -> None:
    op.execute(
        """
        INSERT INTO app_registry_health_checks (
          app_code,
          env_code,
          endpoint_id,
          check_type,
          expected_status,
          expected_json_path,
          expected_json_value,
          timeout_ms,
          interval_seconds,
          severity,
          is_active
        )
        SELECT
          e.app_code,
          e.env_code,
          e.id,
          'http_status',
          200,
          NULL,
          NULL,
          e.timeout_ms,
          CASE
            WHEN e.endpoint_type = 'db_health' THEN 120
            ELSE 60
          END,
          CASE
            WHEN e.endpoint_type = 'db_health' THEN 'warning'
            ELSE 'critical'
          END,
          TRUE
        FROM app_registry_endpoints e
        WHERE e.endpoint_type IN ('health', 'db_health')
          AND e.is_active = TRUE
        ON CONFLICT (app_code, env_code, endpoint_id, check_type) DO UPDATE
        SET
          expected_status = EXCLUDED.expected_status,
          expected_json_path = EXCLUDED.expected_json_path,
          expected_json_value = EXCLUDED.expected_json_value,
          timeout_ms = EXCLUDED.timeout_ms,
          interval_seconds = EXCLUDED.interval_seconds,
          severity = EXCLUDED.severity,
          is_active = EXCLUDED.is_active,
          updated_at = now()
        """
    )

    op.execute(
        """
        INSERT INTO app_registry_openapi_sources (
          app_code,
          env_code,
          endpoint_id,
          openapi_url,
          last_fetched_at,
          last_checksum,
          last_status,
          is_active
        )
        SELECT
          e.app_code,
          e.env_code,
          e.id,
          e.url,
          NULL,
          NULL,
          'unknown',
          TRUE
        FROM app_registry_endpoints e
        WHERE e.endpoint_type = 'openapi'
          AND e.is_active = TRUE
        ON CONFLICT (app_code, env_code, endpoint_id) DO UPDATE
        SET
          openapi_url = EXCLUDED.openapi_url,
          last_status = EXCLUDED.last_status,
          is_active = EXCLUDED.is_active,
          updated_at = now()
        """
    )


def downgrade() -> None:
    op.drop_index(
        "ix_app_registry_openapi_sources_endpoint_id",
        table_name="app_registry_openapi_sources",
    )
    op.drop_index(
        "ix_app_registry_openapi_sources_env_code",
        table_name="app_registry_openapi_sources",
    )
    op.drop_index(
        "ix_app_registry_openapi_sources_app_code",
        table_name="app_registry_openapi_sources",
    )
    op.drop_table("app_registry_openapi_sources")

    op.drop_index(
        "ix_app_registry_health_check_runs_status",
        table_name="app_registry_health_check_runs",
    )
    op.drop_index(
        "ix_app_registry_health_check_runs_started_at",
        table_name="app_registry_health_check_runs",
    )
    op.drop_index(
        "ix_app_registry_health_check_runs_health_check_id",
        table_name="app_registry_health_check_runs",
    )
    op.drop_table("app_registry_health_check_runs")

    op.drop_index(
        "ix_app_registry_health_checks_endpoint_id",
        table_name="app_registry_health_checks",
    )
    op.drop_index(
        "ix_app_registry_health_checks_env_code",
        table_name="app_registry_health_checks",
    )
    op.drop_index(
        "ix_app_registry_health_checks_app_code",
        table_name="app_registry_health_checks",
    )
    op.drop_table("app_registry_health_checks")
