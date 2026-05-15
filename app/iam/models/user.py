from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.page_registry.models.page_registry import Permission

user_permissions = sa.Table(
    "user_permissions",
    Base.metadata,
    sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("users.id", name="fk_user_permissions_user_id_users", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    sa.Column(
        "permission_id",
        sa.Integer,
        sa.ForeignKey(
            "permissions.id",
            name="fk_user_permissions_permission_id_permissions",
            ondelete="CASCADE",
        ),
        primary_key=True,
        nullable=False,
    ),
    sa.Column(
        "granted_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("CURRENT_TIMESTAMP"),
    ),
    sa.Index("ix_user_permissions_permission_id", "permission_id"),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(sa.String(64), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("true"),
    )
    full_name: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    phone: Mapped[str | None] = mapped_column(sa.String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
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

    permissions: Mapped[list[Permission]] = relationship(
        Permission,
        secondary=user_permissions,
        lazy="selectin",
    )


__all__ = ["User", "user_permissions"]
