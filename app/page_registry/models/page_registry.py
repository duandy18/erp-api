from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(128), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )


class PageRegistry(Base):
    __tablename__ = "page_registry"

    code: Mapped[str] = mapped_column(sa.String(128), primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    parent_code: Mapped[str | None] = mapped_column(
        sa.String(128),
        sa.ForeignKey("page_registry.code", ondelete="CASCADE"),
        nullable=True,
    )
    level: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    domain_code: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    show_in_topbar: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("false"),
    )
    show_in_sidebar: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("true"),
    )
    inherit_permissions: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("true"),
    )
    read_permission_id: Mapped[int | None] = mapped_column(
        sa.Integer,
        sa.ForeignKey("permissions.id", ondelete="RESTRICT"),
        nullable=True,
    )
    write_permission_id: Mapped[int | None] = mapped_column(
        sa.Integer,
        sa.ForeignKey("permissions.id", ondelete="RESTRICT"),
        nullable=True,
    )
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
        sa.CheckConstraint("level >= 1", name=sa.schema.conv("ck_page_registry_level_positive")),
        sa.CheckConstraint(
            "length(trim(code)) > 0",
            name=sa.schema.conv("ck_page_registry_code_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name=sa.schema.conv("ck_page_registry_name_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(domain_code)) > 0",
            name=sa.schema.conv("ck_page_registry_domain_code_non_empty"),
        ),
        sa.Index("ix_page_registry_parent_code", "parent_code"),
        sa.Index("ix_page_registry_domain_level_sort", "domain_code", "level", "sort_order"),
    )


class PageRoutePrefix(Base):
    __tablename__ = "page_route_prefixes"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    page_code: Mapped[str] = mapped_column(
        sa.String(128),
        sa.ForeignKey("page_registry.code", ondelete="CASCADE"),
        nullable=False,
    )
    route_prefix: Mapped[str] = mapped_column(sa.String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "page_code",
            "route_prefix",
            name=sa.schema.conv("uq_page_route_prefixes_page_route"),
        ),
        sa.CheckConstraint(
            "length(trim(route_prefix)) > 0",
            name=sa.schema.conv("ck_page_route_prefixes_route_prefix_non_empty"),
        ),
        sa.Index("ix_page_route_prefixes_page_code", "page_code"),
    )


__all__ = ["PageRegistry", "PageRoutePrefix", "Permission"]
