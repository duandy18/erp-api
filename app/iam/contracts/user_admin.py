from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UserCreateIn(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)
    permission_ids: list[int] = Field(default_factory=list)
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None

    model_config = ConfigDict(extra="forbid")


class UserUpdateIn(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None
    is_active: bool | None = None

    model_config = ConfigDict(extra="forbid")


__all__ = ["UserCreateIn", "UserUpdateIn"]
