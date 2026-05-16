# ruff: noqa: E501
"""erp_app_registry_app_metadata_foundation

Revision ID: 0006_app_registry_profile
Revises: 0005_erp_app_registry_admin_page
Create Date: 2026-05-15 22:20:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_app_registry_profile"
down_revision: str | Sequence[str] | None = "0005_erp_app_registry_admin_page"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "app_registry_apps",
        sa.Column("domain_code", sa.String(length=64), server_default="unknown", nullable=False),
    )
    op.add_column(
        "app_registry_apps",
        sa.Column("app_type", sa.String(length=32), server_default="business", nullable=False),
    )
    op.add_column("app_registry_apps", sa.Column("owner_name", sa.String(length=128), nullable=True))
    op.add_column("app_registry_apps", sa.Column("owner_contact", sa.String(length=128), nullable=True))
    op.create_check_constraint(
        "ck_app_registry_apps_domain_code_non_empty",
        "app_registry_apps",
        "length(trim(domain_code)) > 0",
    )
    op.create_check_constraint(
        "ck_app_registry_apps_app_type_known",
        "app_registry_apps",
        "app_type IN ('business', 'control_plane', 'gateway', 'infrastructure')",
    )

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

    op.create_table(
        "app_registry_endpoints",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("component_id", sa.Integer(), nullable=True),
        sa.Column("env_code", sa.String(length=32), nullable=False),
        sa.Column("endpoint_type", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("method", sa.String(length=16), nullable=True),
        sa.Column("path", sa.String(length=256), nullable=True),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.Column("auth_required", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("timeout_ms", sa.Integer(), server_default="5000", nullable=False),
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
            "endpoint_type IN ('web', 'api', 'health', 'db_health', 'openapi', 'metrics', 'docs')",
            name="ck_app_registry_endpoints_endpoint_type_known",
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_app_registry_endpoints_name_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(url)) > 0",
            name="ck_app_registry_endpoints_url_non_empty",
        ),
        sa.CheckConstraint(
            "timeout_ms > 0",
            name="ck_app_registry_endpoints_timeout_positive",
        ),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_endpoints_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["component_id"],
            ["app_registry_components.id"],
            name="fk_app_registry_endpoints_component_id_components",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["env_code"],
            ["app_registry_environments.env_code"],
            name="fk_app_registry_endpoints_env_code_environments",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_endpoints"),
        sa.UniqueConstraint(
            "app_code",
            "env_code",
            "endpoint_type",
            "name",
            name="uq_app_registry_endpoints_app_env_type_name",
        ),
    )
    op.create_index("ix_app_registry_endpoints_app_code", "app_registry_endpoints", ["app_code"])
    op.create_index(
        "ix_app_registry_endpoints_env_type",
        "app_registry_endpoints",
        ["env_code", "endpoint_type"],
    )

    op.create_table(
        "app_registry_databases",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("env_code", sa.String(length=32), nullable=False),
        sa.Column("db_engine", sa.String(length=32), nullable=False),
        sa.Column("db_host_label", sa.String(length=128), nullable=False),
        sa.Column("db_port", sa.Integer(), nullable=False),
        sa.Column("db_name", sa.String(length=128), nullable=False),
        sa.Column("schema_name", sa.String(length=128), nullable=False),
        sa.Column("migration_tool", sa.String(length=64), nullable=True),
        sa.Column("migration_command", sa.String(length=256), nullable=True),
        sa.Column("health_endpoint_id", sa.Integer(), nullable=True),
        sa.Column("secret_ref", sa.String(length=128), nullable=True),
        sa.Column("access_policy", sa.String(length=64), server_default="health_endpoint_only", nullable=False),
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
            "length(trim(db_engine)) > 0",
            name="ck_app_registry_databases_db_engine_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(db_host_label)) > 0",
            name="ck_app_registry_databases_db_host_label_non_empty",
        ),
        sa.CheckConstraint("db_port > 0", name="ck_app_registry_databases_db_port_positive"),
        sa.CheckConstraint(
            "length(trim(db_name)) > 0",
            name="ck_app_registry_databases_db_name_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(schema_name)) > 0",
            name="ck_app_registry_databases_schema_name_non_empty",
        ),
        sa.CheckConstraint(
            "access_policy IN ('metadata_only', 'health_endpoint_only')",
            name="ck_app_registry_databases_access_policy_known",
        ),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_databases_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["env_code"],
            ["app_registry_environments.env_code"],
            name="fk_app_registry_databases_env_code_environments",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["health_endpoint_id"],
            ["app_registry_endpoints.id"],
            name="fk_app_registry_databases_health_endpoint_id_endpoints",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_databases"),
        sa.UniqueConstraint(
            "app_code",
            "env_code",
            "db_name",
            name="uq_app_registry_databases_app_env_db_name",
        ),
    )
    op.create_index("ix_app_registry_databases_app_code", "app_registry_databases", ["app_code"])
    op.create_index("ix_app_registry_databases_env_code", "app_registry_databases", ["env_code"])

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
    op.create_index("ix_app_registry_repositories_app_code", "app_registry_repositories", ["app_code"])

    _seed_app_metadata_foundation()


def _seed_app_metadata_foundation() -> None:
    op.execute(
        """
        UPDATE app_registry_apps
        SET
          domain_code = code,
          app_type = 'business',
          updated_at = now()
        WHERE code IN ('wms', 'pms', 'oms', 'procurement', 'logistics')
        """
    )
    op.execute(
        """
        INSERT INTO app_registry_apps (
          code, name, description, web_path, api_path, local_web_url, local_api_url,
          status, domain_code, app_type, sort_order, is_active
        )
        VALUES (
          'erp',
          'ERP 总控平台',
          '统一入口、身份、应用注册、系统授权、Gateway、审计和总控驾驶舱。',
          '/',
          '/api/erp',
          'http://127.0.0.1:5170',
          'http://127.0.0.1:7990',
          'ready',
          'erp',
          'control_plane',
          0,
          FALSE
        )
        ON CONFLICT (code) DO UPDATE
        SET
          name = EXCLUDED.name,
          description = EXCLUDED.description,
          web_path = EXCLUDED.web_path,
          api_path = EXCLUDED.api_path,
          local_web_url = EXCLUDED.local_web_url,
          local_api_url = EXCLUDED.local_api_url,
          status = EXCLUDED.status,
          domain_code = EXCLUDED.domain_code,
          app_type = EXCLUDED.app_type,
          sort_order = EXCLUDED.sort_order,
          is_active = EXCLUDED.is_active,
          updated_at = now()
        """
    )
    op.execute(
        """
        INSERT INTO app_registry_environments (env_code, name, description, sort_order, is_active)
        VALUES
          ('local', '本地开发', '本机开发和联调环境。', 10, TRUE),
          ('dev', '开发环境', '共享开发环境。', 20, TRUE),
          ('test', '测试环境', '测试验证环境。', 30, TRUE),
          ('staging', '预生产环境', '上线前预生产验证环境。', 40, TRUE),
          ('prod', '生产环境', '正式生产环境。', 50, TRUE)
        ON CONFLICT (env_code) DO UPDATE
        SET
          name = EXCLUDED.name,
          description = EXCLUDED.description,
          sort_order = EXCLUDED.sort_order,
          is_active = EXCLUDED.is_active,
          updated_at = now()
        """
    )
    op.execute(
        """
        INSERT INTO app_registry_app_environments (
          app_code, env_code, display_name, is_default, is_active, notes
        )
        SELECT code, 'local', name || ' local', TRUE, TRUE, '当前第一阶段只登记 local 环境。'
        FROM app_registry_apps
        WHERE code IN ('erp', 'wms', 'pms', 'oms', 'procurement', 'logistics')
        ON CONFLICT (app_code, env_code) DO UPDATE
        SET
          display_name = EXCLUDED.display_name,
          is_default = EXCLUDED.is_default,
          is_active = EXCLUDED.is_active,
          notes = EXCLUDED.notes,
          updated_at = now()
        """
    )
    op.execute(
        """
        INSERT INTO app_registry_components (
          app_code, component_code, component_type, name, description, is_required, is_active, sort_order
        )
        VALUES
          ('erp', 'api', 'api', 'erp-api', 'ERP 控制面后端。', TRUE, TRUE, 10),
          ('erp', 'web', 'web', 'erp-web', 'ERP 控制面前端。', TRUE, TRUE, 20),
          ('erp', 'gateway', 'gateway', 'erp-gateway', 'ERP 本地统一入口 Gateway。', TRUE, TRUE, 30),
          ('wms', 'api', 'api', 'wms-api', 'WMS 后端服务。', TRUE, TRUE, 10),
          ('wms', 'web', 'web', 'wms-web', 'WMS 前端应用。', TRUE, TRUE, 20),
          ('pms', 'api', 'api', 'pms-api', 'PMS 后端服务。', TRUE, TRUE, 10),
          ('pms', 'web', 'web', 'pms-web', 'PMS 前端应用。', TRUE, TRUE, 20),
          ('oms', 'api', 'api', 'oms-api', 'OMS 后端服务。', TRUE, TRUE, 10),
          ('oms', 'web', 'web', 'oms-web', 'OMS 前端应用。', TRUE, TRUE, 20),
          ('procurement', 'api', 'api', 'procurement-api', '采购后端服务。', TRUE, TRUE, 10),
          ('procurement', 'web', 'web', 'procurement-web', '采购前端应用。', TRUE, TRUE, 20),
          ('logistics', 'api', 'api', 'logistics-api', '物流辅助后端服务。', TRUE, TRUE, 10),
          ('logistics', 'web', 'web', 'logistics-web', '物流辅助前端应用。', TRUE, TRUE, 20)
        ON CONFLICT (app_code, component_code) DO UPDATE
        SET
          component_type = EXCLUDED.component_type,
          name = EXCLUDED.name,
          description = EXCLUDED.description,
          is_required = EXCLUDED.is_required,
          is_active = EXCLUDED.is_active,
          sort_order = EXCLUDED.sort_order,
          updated_at = now()
        """
    )
    op.execute(
        """
        INSERT INTO app_registry_endpoints (
          app_code, component_id, env_code, endpoint_type, name, method, path, url,
          auth_required, timeout_ms, is_active, sort_order
        )
        SELECT
          a.code,
          c.id,
          'local',
          'web',
          'Local Web',
          NULL,
          NULL,
          a.local_web_url,
          FALSE,
          5000,
          TRUE,
          10
        FROM app_registry_apps a
        LEFT JOIN app_registry_components c
          ON c.app_code = a.code AND c.component_code = 'web'
        WHERE a.code IN ('erp', 'wms', 'pms', 'oms', 'procurement', 'logistics')
        ON CONFLICT (app_code, env_code, endpoint_type, name) DO UPDATE
        SET
          component_id = EXCLUDED.component_id,
          url = EXCLUDED.url,
          updated_at = now()
        """
    )
    op.execute(
        """
        INSERT INTO app_registry_endpoints (
          app_code, component_id, env_code, endpoint_type, name, method, path, url,
          auth_required, timeout_ms, is_active, sort_order
        )
        SELECT
          a.code,
          c.id,
          'local',
          endpoint.endpoint_type,
          endpoint.name,
          endpoint.method,
          endpoint.path,
          a.local_api_url || endpoint.path,
          FALSE,
          5000,
          TRUE,
          endpoint.sort_order
        FROM app_registry_apps a
        LEFT JOIN app_registry_components c
          ON c.app_code = a.code AND c.component_code = 'api'
        CROSS JOIN (
          VALUES
            ('api', 'Local API', NULL, '', 20),
            ('health', 'Health', 'GET', '/healthz', 30),
            ('db_health', 'DB Health', 'GET', '/health/db', 40),
            ('openapi', 'OpenAPI', 'GET', '/openapi.json', 50)
        ) AS endpoint(endpoint_type, name, method, path, sort_order)
        WHERE a.code IN ('erp', 'wms', 'pms', 'oms', 'procurement', 'logistics')
        ON CONFLICT (app_code, env_code, endpoint_type, name) DO UPDATE
        SET
          component_id = EXCLUDED.component_id,
          method = EXCLUDED.method,
          path = EXCLUDED.path,
          url = EXCLUDED.url,
          updated_at = now()
        """
    )
    op.execute(
        """
        INSERT INTO app_registry_databases (
          app_code, env_code, db_engine, db_host_label, db_port, db_name, schema_name,
          migration_tool, migration_command, health_endpoint_id, secret_ref,
          access_policy, is_active, notes
        )
        VALUES
          ('erp', 'local', 'postgres', '127.0.0.1', 5433, 'erp', 'public', 'alembic', 'make upgrade-dev', (SELECT id FROM app_registry_endpoints WHERE app_code = 'erp' AND env_code = 'local' AND endpoint_type = 'db_health' AND name = 'DB Health'), 'ERP_DATABASE_URL', 'health_endpoint_only', TRUE, '只登记元信息，不保存密码或完整连接串。'),
          ('wms', 'local', 'postgres', '127.0.0.1', 5433, 'wms', 'public', 'alembic', 'make upgrade-dev', (SELECT id FROM app_registry_endpoints WHERE app_code = 'wms' AND env_code = 'local' AND endpoint_type = 'db_health' AND name = 'DB Health'), 'WMS_DATABASE_URL', 'health_endpoint_only', TRUE, '只登记元信息，不允许 ERP 直连业务库查询。'),
          ('pms', 'local', 'postgres', '127.0.0.1', 5433, 'pms', 'public', 'alembic', 'make upgrade-dev', (SELECT id FROM app_registry_endpoints WHERE app_code = 'pms' AND env_code = 'local' AND endpoint_type = 'db_health' AND name = 'DB Health'), 'PMS_DATABASE_URL', 'health_endpoint_only', TRUE, '只登记元信息，不允许 ERP 直连业务库查询。'),
          ('oms', 'local', 'postgres', '127.0.0.1', 5433, 'oms', 'public', 'alembic', 'make upgrade-dev', (SELECT id FROM app_registry_endpoints WHERE app_code = 'oms' AND env_code = 'local' AND endpoint_type = 'db_health' AND name = 'DB Health'), 'OMS_DATABASE_URL', 'health_endpoint_only', TRUE, '只登记元信息，不允许 ERP 直连业务库查询。'),
          ('procurement', 'local', 'postgres', '127.0.0.1', 5433, 'procurement', 'public', 'alembic', 'make upgrade-dev', (SELECT id FROM app_registry_endpoints WHERE app_code = 'procurement' AND env_code = 'local' AND endpoint_type = 'db_health' AND name = 'DB Health'), 'PROCUREMENT_DATABASE_URL', 'health_endpoint_only', TRUE, '只登记元信息，不允许 ERP 直连业务库查询。'),
          ('logistics', 'local', 'postgres', '127.0.0.1', 5433, 'logistics', 'public', 'alembic', 'make upgrade-dev', (SELECT id FROM app_registry_endpoints WHERE app_code = 'logistics' AND env_code = 'local' AND endpoint_type = 'db_health' AND name = 'DB Health'), 'LOGISTICS_DATABASE_URL', 'health_endpoint_only', TRUE, '只登记元信息，不允许 ERP 直连业务库查询。')
        ON CONFLICT (app_code, env_code, db_name) DO UPDATE
        SET
          db_engine = EXCLUDED.db_engine,
          db_host_label = EXCLUDED.db_host_label,
          db_port = EXCLUDED.db_port,
          schema_name = EXCLUDED.schema_name,
          migration_tool = EXCLUDED.migration_tool,
          migration_command = EXCLUDED.migration_command,
          health_endpoint_id = EXCLUDED.health_endpoint_id,
          secret_ref = EXCLUDED.secret_ref,
          access_policy = EXCLUDED.access_policy,
          is_active = EXCLUDED.is_active,
          notes = EXCLUDED.notes,
          updated_at = now()
        """
    )
    op.execute(
        """
        INSERT INTO app_registry_repositories (
          app_code, component_id, repo_type, provider, repo_owner, repo_name,
          default_branch, local_path, ci_workflow_name, is_active
        )
        VALUES
          ('erp', (SELECT id FROM app_registry_components WHERE app_code = 'erp' AND component_code = 'api'), 'api', 'github', 'duandy18', 'erp-api', 'main', '~/erp-api', 'Backend CI', TRUE),
          ('erp', (SELECT id FROM app_registry_components WHERE app_code = 'erp' AND component_code = 'web'), 'web', 'github', 'duandy18', 'erp-web', 'main', '~/erp-web', 'Frontend CI', TRUE),
          ('erp', (SELECT id FROM app_registry_components WHERE app_code = 'erp' AND component_code = 'gateway'), 'gateway', 'github', 'duandy18', 'erp-gateway', 'main', '~/erp-gateway', 'Gateway CI', TRUE),
          ('wms', (SELECT id FROM app_registry_components WHERE app_code = 'wms' AND component_code = 'api'), 'api', 'github', 'duandy18', 'wms-api', 'main', '~/wms-api', 'Backend CI', TRUE),
          ('wms', (SELECT id FROM app_registry_components WHERE app_code = 'wms' AND component_code = 'web'), 'web', 'github', 'duandy18', 'wms-web', 'main', '~/wms-web', 'Frontend CI', TRUE),
          ('pms', (SELECT id FROM app_registry_components WHERE app_code = 'pms' AND component_code = 'api'), 'api', 'github', 'duandy18', 'pms-api', 'main', '~/pms-api', 'Backend CI', TRUE),
          ('pms', (SELECT id FROM app_registry_components WHERE app_code = 'pms' AND component_code = 'web'), 'web', 'github', 'duandy18', 'pms-web', 'main', '~/pms-web', 'Frontend CI', TRUE),
          ('oms', (SELECT id FROM app_registry_components WHERE app_code = 'oms' AND component_code = 'api'), 'api', 'github', 'duandy18', 'oms-api', 'main', '~/oms-api', 'Backend CI', TRUE),
          ('oms', (SELECT id FROM app_registry_components WHERE app_code = 'oms' AND component_code = 'web'), 'web', 'github', 'duandy18', 'oms-web', 'main', '~/oms-web', 'Frontend CI', TRUE),
          ('procurement', (SELECT id FROM app_registry_components WHERE app_code = 'procurement' AND component_code = 'api'), 'api', 'github', 'duandy18', 'procurement-api', 'main', '~/procurement-api', 'Backend CI', TRUE),
          ('procurement', (SELECT id FROM app_registry_components WHERE app_code = 'procurement' AND component_code = 'web'), 'web', 'github', 'duandy18', 'procurement-web', 'main', '~/procurement-web', 'Frontend CI', TRUE),
          ('logistics', (SELECT id FROM app_registry_components WHERE app_code = 'logistics' AND component_code = 'api'), 'api', 'github', 'duandy18', 'logistics-api', 'main', '~/logistics-api', 'Backend CI', TRUE),
          ('logistics', (SELECT id FROM app_registry_components WHERE app_code = 'logistics' AND component_code = 'web'), 'web', 'github', 'duandy18', 'logistics-web', 'main', '~/logistics-web', 'Frontend CI', TRUE)
        ON CONFLICT (app_code, repo_type, repo_name) DO UPDATE
        SET
          component_id = EXCLUDED.component_id,
          provider = EXCLUDED.provider,
          repo_owner = EXCLUDED.repo_owner,
          default_branch = EXCLUDED.default_branch,
          local_path = EXCLUDED.local_path,
          ci_workflow_name = EXCLUDED.ci_workflow_name,
          is_active = EXCLUDED.is_active,
          updated_at = now()
        """
    )


def downgrade() -> None:
    op.drop_index("ix_app_registry_repositories_app_code", table_name="app_registry_repositories")
    op.drop_table("app_registry_repositories")

    op.drop_index("ix_app_registry_databases_env_code", table_name="app_registry_databases")
    op.drop_index("ix_app_registry_databases_app_code", table_name="app_registry_databases")
    op.drop_table("app_registry_databases")

    op.drop_index("ix_app_registry_endpoints_env_type", table_name="app_registry_endpoints")
    op.drop_index("ix_app_registry_endpoints_app_code", table_name="app_registry_endpoints")
    op.drop_table("app_registry_endpoints")

    op.drop_index("ix_app_registry_app_environments_env_code", table_name="app_registry_app_environments")
    op.drop_index("ix_app_registry_app_environments_app_code", table_name="app_registry_app_environments")
    op.drop_table("app_registry_app_environments")

    op.drop_index("ix_app_registry_components_app_code", table_name="app_registry_components")
    op.drop_table("app_registry_components")

    op.drop_table("app_registry_environments")

    op.execute(
        """
        DELETE FROM app_registry_apps
        WHERE code = 'erp'
          AND app_type = 'control_plane'
        """
    )

    op.drop_constraint(
        "ck_app_registry_apps_app_type_known",
        "app_registry_apps",
        type_="check",
    )
    op.drop_constraint(
        "ck_app_registry_apps_domain_code_non_empty",
        "app_registry_apps",
        type_="check",
    )
    op.drop_column("app_registry_apps", "owner_contact")
    op.drop_column("app_registry_apps", "owner_name")
    op.drop_column("app_registry_apps", "app_type")
    op.drop_column("app_registry_apps", "domain_code")
