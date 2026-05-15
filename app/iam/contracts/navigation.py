from __future__ import annotations

from pydantic import BaseModel, Field


class NavigationPageOut(BaseModel):
    code: str
    name: str
    parent_code: str | None
    level: int
    domain_code: str
    show_in_topbar: bool
    show_in_sidebar: bool
    sort_order: int
    is_active: bool
    inherit_permissions: bool
    effective_read_permission: str | None
    effective_write_permission: str | None
    children: list[NavigationPageOut] = Field(default_factory=list)


class NavigationRoutePrefixOut(BaseModel):
    route_prefix: str
    page_code: str
    sort_order: int
    is_active: bool
    effective_read_permission: str | None
    effective_write_permission: str | None


class MyNavigationOut(BaseModel):
    pages: list[NavigationPageOut]
    route_prefixes: list[NavigationRoutePrefixOut]


__all__ = ["MyNavigationOut", "NavigationPageOut", "NavigationRoutePrefixOut"]
