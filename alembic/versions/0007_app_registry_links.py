# ruff: noqa: E501
"""app_registry_gateway_and_dependencies

Revision ID: 0007_app_registry_links
Revises: 0006_app_registry_profile
Create Date: 2026-05-15 23:10:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_app_registry_links"
down_revision: str | Sequence[str] | None = "0006_app_registry_profile"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "app_registry_gateway_bindings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("env_code", sa.String(length=32), nullable=False),
        sa.Column("web_path", sa.String(length=256), nullable=False),
        sa.Column("api_path", sa.String(length=256), nullable=False),
        sa.Column("web_upstream_url", sa.String(length=512), nullable=True),
        sa.Column("api_upstream_url", sa.String(length=512), nullable=True),
        sa.Column("rewrite_mode", sa.String(length=32), server_default="preserve_prefix", nullable=False),
        sa.Column("is_published", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "left(web_path, 1) = '/'",
            name="ck_app_registry_gateway_bindings_web_path_slash",
        ),
        sa.CheckConstraint(
            "left(api_path, 1) = '/'",
            name="ck_app_registry_gateway_bindings_api_path_slash",
        ),
        sa.CheckConstraint(
            "rewrite_mode IN ('preserve_prefix', 'strip_prefix')",
            name="ck_app_registry_gateway_bindings_rewrite_mode_known",
        ),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_gateway_bindings_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["env_code"],
            ["app_registry_environments.env_code"],
            name="fk_app_registry_gateway_bindings_env_code_environments",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_gateway_bindings"),
        sa.UniqueConstraint(
            "app_code",
            "env_code",
            "web_path",
            "api_path",
            name="uq_app_registry_gateway_bindings_app_env_paths",
        ),
    )
    op.create_index(
        "ix_app_registry_gateway_bindings_app_code",
        "app_registry_gateway_bindings",
        ["app_code"],
    )
    op.create_index(
        "ix_app_registry_gateway_bindings_env_code",
        "app_registry_gateway_bindings",
        ["env_code"],
    )

    op.create_table(
        "app_registry_dependencies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_app_code", sa.String(length=64), nullable=False),
        sa.Column("target_app_code", sa.String(length=64), nullable=False),
        sa.Column("dependency_type", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("is_required", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="planned", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "dependency_type IN ('http_api', 'projection_feed', 'webhook', 'file_exchange')",
            name="ck_app_registry_dependencies_dependency_type_known",
        ),
        sa.CheckConstraint(
            "status IN ('planned', 'ready', 'deprecated')",
            name="ck_app_registry_dependencies_status_known",
        ),
        sa.CheckConstraint(
            "length(trim(description)) > 0",
            name="ck_app_registry_dependencies_description_non_empty",
        ),
        sa.ForeignKeyConstraint(
            ["source_app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_dependencies_source_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_dependencies_target_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_dependencies"),
        sa.UniqueConstraint(
            "source_app_code",
            "target_app_code",
            "dependency_type",
            name="uq_app_registry_dependencies_source_target_type",
        ),
    )
    op.create_index(
        "ix_app_registry_dependencies_source_app_code",
        "app_registry_dependencies",
        ["source_app_code"],
    )
    op.create_index(
        "ix_app_registry_dependencies_target_app_code",
        "app_registry_dependencies",
        ["target_app_code"],
    )

    _seed_gateway_bindings_and_dependencies()


def _seed_gateway_bindings_and_dependencies() -> None:
    op.execute(
        """
        INSERT INTO app_registry_gateway_bindings (
          app_code,
          env_code,
          web_path,
          api_path,
          web_upstream_url,
          api_upstream_url,
          rewrite_mode,
          is_published,
          published_at,
          is_active
        )
        VALUES
          (
            'erp',
            'local',
            '/',
            '/api/erp',
            'http://host.docker.internal:5170',
            'http://host.docker.internal:7990',
            'preserve_prefix',
            TRUE,
            now(),
            TRUE
          ),
          (
            'wms',
            'local',
            '/wms',
            '/api/wms',
            'http://host.docker.internal:5173',
            'http://host.docker.internal:8000',
            'preserve_prefix',
            FALSE,
            NULL,
            TRUE
          ),
          (
            'pms',
            'local',
            '/pms',
            '/api/pms',
            'http://host.docker.internal:5174',
            'http://host.docker.internal:8005',
            'preserve_prefix',
            FALSE,
            NULL,
            TRUE
          ),
          (
            'oms',
            'local',
            '/oms',
            '/api/oms',
            'http://host.docker.internal:5175',
            'http://host.docker.internal:8010',
            'preserve_prefix',
            FALSE,
            NULL,
            TRUE
          ),
          (
            'procurement',
            'local',
            '/procurement',
            '/api/procurement',
            'http://host.docker.internal:5176',
            'http://host.docker.internal:8015',
            'preserve_prefix',
            FALSE,
            NULL,
            TRUE
          ),
          (
            'logistics',
            'local',
            '/logistics',
            '/api/logistics',
            'http://host.docker.internal:5177',
            'http://host.docker.internal:8020',
            'preserve_prefix',
            FALSE,
            NULL,
            TRUE
          )
        ON CONFLICT (app_code, env_code, web_path, api_path) DO UPDATE
        SET
          web_upstream_url = EXCLUDED.web_upstream_url,
          api_upstream_url = EXCLUDED.api_upstream_url,
          rewrite_mode = EXCLUDED.rewrite_mode,
          is_published = EXCLUDED.is_published,
          published_at = EXCLUDED.published_at,
          is_active = EXCLUDED.is_active,
          updated_at = now()
        """
    )
    op.execute(
        """
        INSERT INTO app_registry_dependencies (
          source_app_code,
          target_app_code,
          dependency_type,
          description,
          is_required,
          status,
          is_active
        )
        VALUES
          (
            'wms',
            'pms',
            'projection_feed',
            'WMS 读取 PMS 商品主数据投影和校验合同。',
            TRUE,
            'ready',
            TRUE
          ),
          (
            'oms',
            'pms',
            'http_api',
            'OMS 读取 PMS 商品、FSKU 与编码映射。',
            TRUE,
            'ready',
            TRUE
          ),
          (
            'procurement',
            'wms',
            'http_api',
            '采购系统与 WMS 采购入库联动。',
            TRUE,
            'planned',
            TRUE
          ),
          (
            'logistics',
            'wms',
            'http_api',
            '物流辅助系统读取 WMS 发货交接数据。',
            TRUE,
            'ready',
            TRUE
          )
        ON CONFLICT (source_app_code, target_app_code, dependency_type) DO UPDATE
        SET
          description = EXCLUDED.description,
          is_required = EXCLUDED.is_required,
          status = EXCLUDED.status,
          is_active = EXCLUDED.is_active,
          updated_at = now()
        """
    )


def downgrade() -> None:
    op.drop_index(
        "ix_app_registry_dependencies_target_app_code",
        table_name="app_registry_dependencies",
    )
    op.drop_index(
        "ix_app_registry_dependencies_source_app_code",
        table_name="app_registry_dependencies",
    )
    op.drop_table("app_registry_dependencies")

    op.drop_index(
        "ix_app_registry_gateway_bindings_env_code",
        table_name="app_registry_gateway_bindings",
    )
    op.drop_index(
        "ix_app_registry_gateway_bindings_app_code",
        table_name="app_registry_gateway_bindings",
    )
    op.drop_table("app_registry_gateway_bindings")
