from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.admin.contracts.user_permission_matrix_update import UserPermissionMatrixUpdateIn
from app.iam.models.user import User, user_permissions
from app.iam.repositories.user_repository import UserRepository
from app.iam.services.user_errors import NotFoundError


class UserPermissionMatrixWriteService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save_matrix_for_user(
        self,
        *,
        user_id: int,
        body: UserPermissionMatrixUpdateIn,
    ) -> User:
        repo = UserRepository(self.db)
        user = repo.get_user(user_id)
        if not user:
            raise NotFoundError("用户不存在")

        root_rows = (
            self.db.execute(
                text(
                    """
                    SELECT
                      pr.code AS page_code,
                      pr.read_permission_id,
                      pr.write_permission_id
                    FROM page_registry pr
                    WHERE pr.is_active = true
                      AND pr.level = 1
                      AND pr.inherit_permissions = false
                    """
                )
            )
            .mappings()
            .all()
        )

        page_permission_ids: dict[str, tuple[int | None, int | None]] = {
            str(row["page_code"]): (
                int(row["read_permission_id"]) if row["read_permission_id"] is not None else None,
                int(row["write_permission_id"]) if row["write_permission_id"] is not None else None,
            )
            for row in root_rows
        }

        page_codes = {page.page_code for page in body.pages}
        unknown_page_codes = page_codes - set(page_permission_ids)
        if unknown_page_codes:
            raise NotFoundError("页面不存在")

        managed_permission_ids = {
            permission_id
            for pair in page_permission_ids.values()
            for permission_id in pair
            if permission_id is not None
        }

        current_rows = (
            self.db.execute(
                text(
                    """
                    SELECT permission_id
                    FROM user_permissions
                    WHERE user_id = :user_id
                    """
                ),
                {"user_id": int(user_id)},
            )
            .mappings()
            .all()
        )
        next_permission_ids = {int(row["permission_id"]) for row in current_rows}
        next_permission_ids -= managed_permission_ids

        for page in body.pages:
            read_permission_id, write_permission_id = page_permission_ids[page.page_code]
            if page.can_read and read_permission_id is not None:
                next_permission_ids.add(read_permission_id)
            if page.can_write:
                if read_permission_id is not None:
                    next_permission_ids.add(read_permission_id)
                if write_permission_id is not None:
                    next_permission_ids.add(write_permission_id)

        self.db.execute(user_permissions.delete().where(user_permissions.c.user_id == int(user_id)))
        for permission_id in sorted(next_permission_ids):
            self.db.execute(
                user_permissions.insert().values(
                    user_id=int(user_id),
                    permission_id=int(permission_id),
                )
            )

        self.db.commit()
        self.db.refresh(user)
        return user


__all__ = ["UserPermissionMatrixWriteService"]
