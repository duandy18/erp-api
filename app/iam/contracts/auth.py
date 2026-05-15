from __future__ import annotations

from pydantic import BaseModel, Field


class UserLoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None


__all__ = ["TokenOut", "UserLoginIn"]
