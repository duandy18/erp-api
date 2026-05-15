from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    is_active: bool
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None
    permissions: list[str] = Field(default_factory=list)


class UserMeOut(BaseModel):
    id: int
    username: str
    permissions: list[str]


__all__ = ["UserMeOut", "UserOut"]
