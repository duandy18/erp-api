from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AppRegistryApp(Base):
    __tablename__ = "app_registry_apps"

    code: Mapped[str] = mapped_column(sa.String(64), primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    description: Mapped[str] = mapped_column(sa.String(512), nullable=False)
    web_path: Mapped[str] = mapped_column(sa.String(256), nullable=False)
    api_path: Mapped[str] = mapped_column(sa.String(256), nullable=False)
    local_web_url: Mapped[str] = mapped_column(sa.String(256), nullable=False)
    local_api_url: Mapped[str] = mapped_column(sa.String(256), nullable=False)
    status: Mapped[str] = mapped_column(sa.String(32), nullable=False, server_default="ready")
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
            "length(trim(code)) > 0",
            name=sa.schema.conv("ck_app_registry_apps_code_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name=sa.schema.conv("ck_app_registry_apps_name_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(description)) > 0",
            name=sa.schema.conv("ck_app_registry_apps_description_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(web_path)) > 0",
            name=sa.schema.conv("ck_app_registry_apps_web_path_non_empty"),
        ),
        sa.CheckConstraint(
            "length(trim(api_path)) > 0",
            name=sa.schema.conv("ck_app_registry_apps_api_path_non_empty"),
        ),
        sa.CheckConstraint(
            "status IN ('ready', 'planned')",
            name=sa.schema.conv("ck_app_registry_apps_status_known"),
        ),
        sa.Index("ix_app_registry_apps_active_sort", "is_active", "sort_order"),
    )


__all__ = ["AppRegistryApp"]
