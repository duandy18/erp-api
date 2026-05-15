from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.admin.contracts.user_permission_matrix import (
    PagePermissionCellOut,
    PermissionMatrixPageOut,
    PermissionMatrixRowOut,
    UserPermissionMatrixOut,
)
from app.iam.models.user import User
from app.iam.services.user_permission_service import get_user_permissions


class UserPermissionMatrixService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _list_root_pages(self) -> list[dict[str, Any]]:
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT
                      pr.code,
                      pr.name,
                      pr.sort_order,
                      rp.name AS read_permission,
                      wp.name AS write_permission
                    FROM page_registry pr
                    LEFT JOIN permissions rp ON rp.id = pr.read_permission_id
                    LEFT JOIN permissions wp ON wp.id = pr.write_permission_id
                    WHERE pr.is_active = true
                      AND pr.level = 1
                      AND pr.inherit_permissions = false
                    ORDER BY pr.sort_order ASC, pr.code ASC
                    """
                )
            )
            .mappings()
            .all()
        )
        return [dict(row) for row in rows]

    def get_matrix(self) -> UserPermissionMatrixOut:
        root_pages = self._list_root_pages()
        pages = [
            PermissionMatrixPageOut(
                page_code=str(row["code"]),
                page_name=str(row["name"]),
                sort_order=int(row["sort_order"] or 0),
            )
            for row in root_pages
        ]

        users = self.db.query(User).order_by(User.id.asc()).all()
        user_rows = [self._build_user_row(user, root_pages) for user in users]

        return UserPermissionMatrixOut(pages=pages, users=user_rows)

    def _build_user_row(
        self,
        user: User,
        root_pages: list[dict[str, Any]],
    ) -> PermissionMatrixRowOut:
        permission_names = set(get_user_permissions(self.db, user))
        cells: dict[str, PagePermissionCellOut] = {}

        for row in root_pages:
            page_code = str(row["code"])
            read_permission = row.get("read_permission")
            write_permission = row.get("write_permission")
            can_write = bool(write_permission and write_permission in permission_names)
            can_read = can_write or bool(read_permission and read_permission in permission_names)
            cells[page_code] = PagePermissionCellOut(read=can_read, write=can_write)

        return PermissionMatrixRowOut(
            user_id=int(user.id),
            username=str(user.username),
            full_name=user.full_name,
            is_active=bool(user.is_active),
            pages=cells,
        )


__all__ = ["UserPermissionMatrixService"]
