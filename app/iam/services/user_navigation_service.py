from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.iam.contracts.navigation import (
    MyNavigationOut,
    NavigationPageOut,
    NavigationRoutePrefixOut,
)
from app.iam.models.user import User
from app.iam.repositories.navigation_repository import NavigationRepository
from app.iam.services.user_permission_service import get_user_permissions


def _compute_effective_permissions(
    rows: list[dict[str, Any]],
) -> dict[str, tuple[str | None, str | None]]:
    by_code = {str(row["code"]): row for row in rows}
    cache: dict[str, tuple[str | None, str | None]] = {}

    def resolve(code: str) -> tuple[str | None, str | None]:
        if code in cache:
            return cache[code]

        row = by_code[code]
        if not bool(row.get("inherit_permissions")):
            value = (
                row.get("self_read_permission"),
                row.get("self_write_permission"),
            )
        else:
            parent_code = row.get("parent_code")
            value = resolve(str(parent_code)) if parent_code and str(parent_code) in by_code else (
                None,
                None,
            )

        cache[code] = value
        return value

    for page_code in by_code:
        resolve(page_code)

    return cache


class UserNavigationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = NavigationRepository(db)

    def get_navigation_for_user(self, user: User) -> MyNavigationOut:
        page_rows = self.repo.list_pages()
        route_rows = self.repo.list_route_prefixes()
        effective = _compute_effective_permissions(page_rows)
        user_permission_set = set(get_user_permissions(self.db, user))

        allowed_codes: set[str] = set()
        for row in page_rows:
            page_code = str(row["code"])
            read_permission, write_permission = effective.get(page_code, (None, None))
            if (
                read_permission in user_permission_set
                or write_permission in user_permission_set
                or (read_permission is None and write_permission is None)
            ):
                allowed_codes.add(page_code)

        allowed_rows = [row for row in page_rows if str(row["code"]) in allowed_codes]
        page_by_code: dict[str, NavigationPageOut] = {}

        for row in allowed_rows:
            code = str(row["code"])
            read_permission, write_permission = effective.get(code, (None, None))
            page_by_code[code] = NavigationPageOut(
                code=code,
                name=str(row["name"]),
                parent_code=row["parent_code"],
                level=int(row["level"]),
                domain_code=str(row["domain_code"]),
                show_in_topbar=bool(row["show_in_topbar"]),
                show_in_sidebar=bool(row["show_in_sidebar"]),
                sort_order=int(row["sort_order"]),
                is_active=bool(row["is_active"]),
                inherit_permissions=bool(row["inherit_permissions"]),
                effective_read_permission=read_permission,
                effective_write_permission=write_permission,
                children=[],
            )

        roots: list[NavigationPageOut] = []
        for page in page_by_code.values():
            if page.parent_code and page.parent_code in page_by_code:
                page_by_code[page.parent_code].children.append(page)
            else:
                roots.append(page)

        def sort_tree(page: NavigationPageOut) -> None:
            page.children.sort(key=lambda item: (item.sort_order, item.code))
            for child in page.children:
                sort_tree(child)

        roots.sort(key=lambda item: (item.sort_order, item.code))
        for root in roots:
            sort_tree(root)

        route_outputs: list[NavigationRoutePrefixOut] = []
        for row in route_rows:
            page_code = str(row["page_code"])
            if page_code not in allowed_codes:
                continue
            read_permission, write_permission = effective.get(page_code, (None, None))
            route_outputs.append(
                NavigationRoutePrefixOut(
                    route_prefix=str(row["route_prefix"]),
                    page_code=page_code,
                    sort_order=int(row.get("sort_order") or 0),
                    is_active=bool(row.get("is_active", True)),
                    effective_read_permission=read_permission,
                    effective_write_permission=write_permission,
                )
            )

        return MyNavigationOut(pages=roots, route_prefixes=route_outputs)


__all__ = ["UserNavigationService"]
