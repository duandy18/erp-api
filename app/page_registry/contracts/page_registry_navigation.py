from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ErpNavigationPageOut(BaseModel):
    code: str
    name: str
    parent_code: str | None = None
    level: int = Field(ge=1)
    domain_code: str
    show_in_topbar: bool
    show_in_sidebar: bool
    sort_order: int
    route_prefixes: list[str] = Field(default_factory=list)
    primary_route: str | None = None
    children: list[ErpNavigationPageOut] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class ErpNavigationOut(BaseModel):
    items: list[ErpNavigationPageOut] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


__all__ = ["ErpNavigationOut", "ErpNavigationPageOut"]
