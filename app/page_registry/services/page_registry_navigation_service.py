from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy.orm import Session

from app.page_registry.contracts.page_registry_navigation import (
    ErpNavigationOut,
    ErpNavigationPageOut,
)
from app.page_registry.repositories.page_registry_repository import PageRegistryRepository


def _page_from_row(
    row: dict[str, Any],
    *,
    route_prefixes: list[str],
) -> ErpNavigationPageOut:
    primary_route = route_prefixes[0] if route_prefixes else None

    return ErpNavigationPageOut(
        code=str(row["code"]),
        name=str(row["name"]),
        parent_code=row["parent_code"],
        level=int(row["level"]),
        domain_code=str(row["domain_code"]),
        show_in_topbar=bool(row["show_in_topbar"]),
        show_in_sidebar=bool(row["show_in_sidebar"]),
        sort_order=int(row["sort_order"]),
        route_prefixes=route_prefixes,
        primary_route=primary_route,
        children=[],
    )


class PageRegistryNavigationService:
    def __init__(self, db: Session) -> None:
        self.repo = PageRegistryRepository(db)

    def list_navigation(self) -> ErpNavigationOut:
        page_rows = self.repo.list_sidebar_pages()
        route_rows = self.repo.list_route_prefixes()

        routes_by_page: dict[str, list[str]] = defaultdict(list)
        for route in route_rows:
            routes_by_page[str(route["page_code"])].append(str(route["route_prefix"]))

        pages_by_code = {
            str(row["code"]): _page_from_row(
                row,
                route_prefixes=routes_by_page.get(str(row["code"]), []),
            )
            for row in page_rows
        }

        roots: list[ErpNavigationPageOut] = []

        for page in pages_by_code.values():
            if page.parent_code and page.parent_code in pages_by_code:
                pages_by_code[page.parent_code].children.append(page)
            else:
                roots.append(page)

        def sort_children(page: ErpNavigationPageOut) -> None:
            page.children.sort(key=lambda item: (item.sort_order, item.code))
            for child in page.children:
                sort_children(child)

        roots.sort(key=lambda item: (item.sort_order, item.code))
        for root in roots:
            sort_children(root)

        return ErpNavigationOut(items=roots)


__all__ = ["PageRegistryNavigationService"]
