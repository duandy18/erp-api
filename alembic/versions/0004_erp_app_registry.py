"""erp_app_registry

Revision ID: 0004_erp_app_registry
Revises: 0003_erp_user_management
Create Date: 2026-05-15 19:20:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_erp_app_registry"
down_revision: str | Sequence[str] | None = "0003_erp_user_management"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "app_registry_apps",
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("web_path", sa.String(length=256), nullable=False),
        sa.Column("api_path", sa.String(length=256), nullable=False),
        sa.Column("local_web_url", sa.String(length=256), nullable=False),
        sa.Column("local_api_url", sa.String(length=256), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="ready", nullable=False),
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
            "length(trim(code)) > 0",
            name="ck_app_registry_apps_code_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_app_registry_apps_name_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(description)) > 0",
            name="ck_app_registry_apps_description_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(web_path)) > 0",
            name="ck_app_registry_apps_web_path_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(api_path)) > 0",
            name="ck_app_registry_apps_api_path_non_empty",
        ),
        sa.CheckConstraint(
            "status IN ('ready', 'planned')",
            name="ck_app_registry_apps_status_known",
        ),
        sa.PrimaryKeyConstraint("code", name="pk_app_registry_apps"),
    )
    op.create_index(
        "ix_app_registry_apps_active_sort",
        "app_registry_apps",
        ["is_active", "sort_order"],
    )

    op.execute(
        """
        INSERT INTO app_registry_apps (
          code,
          name,
          description,
          web_path,
          api_path,
          local_web_url,
          local_api_url,
          status,
          sort_order,
          is_active
        )
        VALUES
          (
            'wms',
            'WMS 仓储执行系统',
            '库存、入库、出库、仓内执行。',
            '/wms',
            '/api/wms',
            'http://127.0.0.1:5173',
            'http://127.0.0.1:8000',
            'ready',
            10,
            TRUE
          ),
          (
            'pms',
            'PMS 商品主数据系统',
            '商品、条码、单位、供应商、SKU 编码。',
            '/pms',
            '/api/pms',
            'http://127.0.0.1:5174',
            'http://127.0.0.1:8005',
            'ready',
            20,
            TRUE
          ),
          (
            'oms',
            'OMS 订单系统',
            '平台订单、FSKU、订单投影与履约入口。',
            '/oms',
            '/api/oms',
            'http://127.0.0.1:5175',
            'http://127.0.0.1:8010',
            'ready',
            30,
            TRUE
          ),
          (
            'procurement',
            'Procurement 采购系统',
            '采购单、采购履约、WMS 收货联动。',
            '/procurement',
            '/api/procurement',
            'http://127.0.0.1:5176',
            'http://127.0.0.1:8015',
            'ready',
            40,
            TRUE
          ),
          (
            'logistics',
            'Logistics 物流辅助系统',
            '发货请求、运价、面单、物流交接。',
            '/logistics',
            '/api/logistics',
            'http://127.0.0.1:5177',
            'http://127.0.0.1:8020',
            'ready',
            50,
            TRUE
          )
        ON CONFLICT (code) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index("ix_app_registry_apps_active_sort", table_name="app_registry_apps")
    op.drop_table("app_registry_apps")
