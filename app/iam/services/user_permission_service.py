from __future__ import annotations

from sqlalchemy.orm import Session

from app.iam.models.user import User, user_permissions
from app.iam.services.user_errors import AuthorizationError
from app.page_registry.models.page_registry import Permission


def get_user_permissions(db: Session, user: User) -> list[str]:
    rows = (
        db.query(Permission.name)
        .join(user_permissions, user_permissions.c.permission_id == Permission.id)
        .filter(user_permissions.c.user_id == int(user.id))
        .order_by(Permission.name.asc())
        .all()
    )
    return [str(row[0]) for row in rows]


def check_user_permission(db: Session, user: User, required: list[str]) -> None:
    current = set(get_user_permissions(db, user))
    if not any(item in current for item in required):
        raise AuthorizationError("当前用户无权访问该资源")


__all__ = ["check_user_permission", "get_user_permissions"]
