from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AppRegistryAppOut(BaseModel):
    code: str
    name: str
    description: str
    web_path: str
    api_path: str
    local_web_url: str
    local_api_url: str
    status: str
    sort_order: int
    is_active: bool

    model_config = ConfigDict(extra="forbid")


class AppRegistryAppsOut(BaseModel):
    apps: list[AppRegistryAppOut] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


__all__ = ["AppRegistryAppOut", "AppRegistryAppsOut"]
