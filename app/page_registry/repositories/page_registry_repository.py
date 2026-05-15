from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class PageRegistryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_sidebar_pages(self) -> list[dict[str, Any]]:
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT
                      code,
                      name,
                      parent_code,
                      level,
                      domain_code,
                      show_in_topbar,
                      show_in_sidebar,
                      sort_order
                    FROM page_registry
                    WHERE is_active = true
                      AND show_in_sidebar = true
                    ORDER BY
                      level ASC,
                      parent_code NULLS FIRST,
                      sort_order ASC,
                      code ASC
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
        return [dict(row) for row in rows]


__all__ = ["PageRegistryRepository"]
