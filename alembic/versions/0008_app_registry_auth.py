# ruff: noqa: E501
"""app_registry_service_auth_metadata

Revision ID: 0008_app_registry_auth
Revises: 0007_app_registry_links
Create Date: 2026-05-15 23:45:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008_app_registry_auth"
down_revision: str | Sequence[str] | None = "0007_app_registry_links"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "app_registry_service_clients",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("app_code", sa.String(length=64), nullable=False),
        sa.Column("client_code", sa.String(length=64), nullable=False),
        sa.Column("client_name", sa.String(length=128), nullable=False),
        sa.Column("auth_type", sa.String(length=32), server_default="none", nullable=False),
        sa.Column("secret_ref", sa.String(length=128), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "auth_type IN ('none', 'static_token', 'client_credentials')",
            name="ck_app_registry_service_clients_auth_type_known",
        ),
        sa.CheckConstraint(
            "length(trim(client_code)) > 0",
            name="ck_app_registry_service_clients_client_code_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(client_name)) > 0",
            name="ck_app_registry_service_clients_client_name_non_empty",
        ),
        sa.ForeignKeyConstraint(
            ["app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_service_clients_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_service_clients"),
        sa.UniqueConstraint(
            "app_code",
            "client_code",
            name="uq_app_registry_service_clients_app_client",
        ),
    )
    op.create_index(
        "ix_app_registry_service_clients_app_code",
        "app_registry_service_clients",
        ["app_code"],
    )

    op.create_table(
        "app_registry_service_permissions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("source_app_code", sa.String(length=64), nullable=False),
        sa.Column("target_app_code", sa.String(length=64), nullable=False),
        sa.Column("permission_code", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "length(trim(permission_code)) > 0",
            name="ck_app_registry_service_permissions_permission_code_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(description)) > 0",
            name="ck_app_registry_service_permissions_description_non_empty",
        ),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["app_registry_service_clients.id"],
            name="fk_app_registry_service_permissions_client_id_clients",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_service_permissions_source_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_app_code"],
            ["app_registry_apps.code"],
            name="fk_app_registry_service_permissions_target_app_code_apps",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_app_registry_service_permissions"),
        sa.UniqueConstraint(
            "client_id",
            "permission_code",
            name="uq_app_registry_service_permissions_client_permission",
        ),
    )
    op.create_index(
        "ix_app_registry_service_permissions_client_id",
        "app_registry_service_permissions",
        ["client_id"],
    )
    op.create_index(
        "ix_app_registry_service_permissions_source_app_code",
        "app_registry_service_permissions",
        ["source_app_code"],
    )
    op.create_index(
        "ix_app_registry_service_permissions_target_app_code",
        "app_registry_service_permissions",
        ["target_app_code"],
    )

    _seed_service_auth_metadata()


def _seed_service_auth_metadata() -> None:
    op.execute(
        """
        INSERT INTO app_registry_service_clients (
          app_code,
          client_code,
          client_name,
          auth_type,
          secret_ref,
          is_active
        )
        VALUES
          ('wms', 'wms-service', 'WMS Service Client', 'none', NULL, FALSE),
          ('pms', 'pms-service', 'PMS Service Client', 'none', NULL, FALSE),
          ('oms', 'oms-service', 'OMS Service Client', 'none', NULL, FALSE),
          (
            'procurement',
            'procurement-service',
            'Procurement Service Client',
            'none',
            NULL,
            FALSE
          ),
          (
            'logistics',
            'logistics-service',
            'Logistics Service Client',
            'none',
            NULL,
            FALSE
          )
        ON CONFLICT (app_code, client_code) DO UPDATE
        SET
          client_name = EXCLUDED.client_name,
          auth_type = EXCLUDED.auth_type,
          secret_ref = EXCLUDED.secret_ref,
          is_active = EXCLUDED.is_active,
          updated_at = now()
        """
    )
    op.execute(
        """
        INSERT INTO app_registry_service_permissions (
          client_id,
          source_app_code,
          target_app_code,
          permission_code,
          description,
          is_active
        )
        VALUES
          (
            (SELECT id FROM app_registry_service_clients WHERE app_code = 'wms' AND client_code = 'wms-service'),
            'wms',
            'pms',
            'pms.read.items',
            'WMS 读取 PMS 商品主数据。',
            FALSE
          ),
          (
            (SELECT id FROM app_registry_service_clients WHERE app_code = 'oms' AND client_code = 'oms-service'),
            'oms',
            'pms',
            'pms.read.items',
            'OMS 读取 PMS 商品主数据。',
            FALSE
          ),
          (
            (SELECT id FROM app_registry_service_clients WHERE app_code = 'procurement' AND client_code = 'procurement-service'),
            'procurement',
            'wms',
            'wms.write.inbound',
            '采购系统写入 WMS 入库联动。',
            FALSE
          ),
          (
            (SELECT id FROM app_registry_service_clients WHERE app_code = 'logistics' AND client_code = 'logistics-service'),
            'logistics',
            'wms',
            'wms.read.shipping_handoffs',
            '物流辅助读取 WMS 发货交接。',
            FALSE
          )
        ON CONFLICT (client_id, permission_code) DO UPDATE
        SET
          source_app_code = EXCLUDED.source_app_code,
          target_app_code = EXCLUDED.target_app_code,
          description = EXCLUDED.description,
          is_active = EXCLUDED.is_active,
          updated_at = now()
        """
    )


def downgrade() -> None:
    op.drop_index(
        "ix_app_registry_service_permissions_target_app_code",
        table_name="app_registry_service_permissions",
    )
    op.drop_index(
        "ix_app_registry_service_permissions_source_app_code",
        table_name="app_registry_service_permissions",
    )
    op.drop_index(
        "ix_app_registry_service_permissions_client_id",
        table_name="app_registry_service_permissions",
    )
    op.drop_table("app_registry_service_permissions")

    op.drop_index(
        "ix_app_registry_service_clients_app_code",
        table_name="app_registry_service_clients",
    )
    op.drop_table("app_registry_service_clients")
