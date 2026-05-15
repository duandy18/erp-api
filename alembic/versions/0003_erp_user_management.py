"""erp_user_management

Revision ID: 0003_erp_user_management
Revises: 0002_erp_page_registry
Create Date: 2026-05-15 18:25:00.000000

"""

from __future__ import annotations

import base64
import hashlib
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_erp_user_management"
down_revision: str | Sequence[str] | None = "0002_erp_page_registry"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _password_hash(password: str) -> str:
    salt = "erp-admin-default"
    iterations = 120_000
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt}${_b64url_encode(digest)}"


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("full_name", sa.String(length=128), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )

    op.create_table(
        "user_permissions",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.Column(
            "granted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_user_permissions_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            name="fk_user_permissions_permission_id_permissions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "permission_id", name="pk_user_permissions"),
    )
    op.create_index("ix_user_permissions_permission_id", "user_permissions", ["permission_id"])

    op.execute(
        sa.text(
            """
            INSERT INTO users (
              username,
              password_hash,
              is_active,
              full_name,
              phone,
              email
            )
            VALUES (
              'admin',
              :password_hash,
              TRUE,
              '系统管理员',
              NULL,
              NULL
            )
            ON CONFLICT (username) DO UPDATE SET
              password_hash = EXCLUDED.password_hash,
              is_active = TRUE,
              full_name = COALESCE(users.full_name, EXCLUDED.full_name)
            """
        ).bindparams(password_hash=_password_hash("admin123"))
    )

    op.execute(
        """
        INSERT INTO user_permissions (user_id, permission_id)
        SELECT u.id, p.id
        FROM users u
        CROSS JOIN permissions p
        WHERE u.username = 'admin'
          AND p.name IN (
            'page.erp.portal.read',
            'page.erp.portal.write',
            'page.erp.apps.read',
            'page.erp.apps.write',
            'page.erp.cockpit.read',
            'page.erp.cockpit.write',
            'page.erp.system.read',
            'page.erp.system.write'
          )
        ON CONFLICT (user_id, permission_id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index("ix_user_permissions_permission_id", table_name="user_permissions")
    op.drop_table("user_permissions")
    op.drop_table("users")
