from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class NavigationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_pages(self) -> list[dict[str, Any]]:
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT
                      pr.code,
                      pr.name,
                      pr.parent_code,
                      pr.level,
                      pr.domain_code,
                      pr.show_in_topbar,
                      pr.show_in_sidebar,
                      pr.sort_order,
                      pr.is_active,
                      pr.inherit_permissions,
                      rp.name AS self_read_permission,
                      wp.name AS self_write_permission
                    FROM page_registry pr
                    LEFT JOIN permissions rp ON rp.id = pr.read_permission_id
                    LEFT JOIN permissions wp ON wp.id = pr.write_permission_id
                    WHERE pr.is_active = true
                    ORDER BY pr.level ASC, pr.sort_order ASC, pr.code ASC
                    """
                )
            )
            .mappings()
            .all()
        )
        return [dict(row) for row in rows]

    def list_route_prefixes(self) -> list[dict[str, Any]]:
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT
                      page_code,
                      route_prefix
                    FROM page_route_prefixes
                    ORDER BY page_code ASC, route_prefix ASC
                    """
                )
            )
            .mappings()
            .all()
        )
        return [
            {
                "page_code": str(row["page_code"]),
                "route_prefix": str(row["route_prefix"]),
                "sort_order": 0,
                "is_active": True,
            }
            for row in rows
        ]


__all__ = ["NavigationRepository"]
