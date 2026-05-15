from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class UserPermissionMatrixPageUpdateIn(BaseModel):
    page_code: str
    can_read: bool
    can_write: bool

    model_config = ConfigDict(extra="forbid")


class UserPermissionMatrixUpdateIn(BaseModel):
    pages: list[UserPermissionMatrixPageUpdateIn]

    model_config = ConfigDict(extra="forbid")


__all__ = ["UserPermissionMatrixPageUpdateIn", "UserPermissionMatrixUpdateIn"]
