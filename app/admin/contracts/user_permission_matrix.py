from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PagePermissionCellOut(BaseModel):
    read: bool
    write: bool

    model_config = ConfigDict(extra="forbid")


class PermissionMatrixPageOut(BaseModel):
    page_code: str
    page_name: str
    sort_order: int

    model_config = ConfigDict(extra="forbid")


class PermissionMatrixRowOut(BaseModel):
    user_id: int
    username: str
    full_name: str | None = None
    is_active: bool
    pages: dict[str, PagePermissionCellOut] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


class UserPermissionMatrixOut(BaseModel):
    pages: list[PermissionMatrixPageOut] = Field(default_factory=list)
    users: list[PermissionMatrixRowOut] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


__all__ = [
    "PagePermissionCellOut",
    "PermissionMatrixPageOut",
    "PermissionMatrixRowOut",
    "UserPermissionMatrixOut",
]
