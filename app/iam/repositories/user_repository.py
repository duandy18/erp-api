from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.iam.models.user import User, user_permissions
from app.iam.services.user_errors import DuplicateUserError, NotFoundError
from app.page_registry.models.page_registry import Permission


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_users(self) -> list[User]:
        return self.db.query(User).order_by(User.id.asc()).all()

    def get_user(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == int(user_id)).one_or_none()

    def get_user_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).one_or_none()

    def list_permissions_by_ids(self, permission_ids: list[int]) -> list[Permission]:
        distinct_ids = sorted({int(item) for item in permission_ids})
        if not distinct_ids:
            return []

        rows = (
            self.db.query(Permission)
            .filter(Permission.id.in_(distinct_ids))
            .order_by(Permission.id.asc())
            .all()
        )

        if len(rows) != len(distinct_ids):
            raise NotFoundError("权限不存在")

        return rows

    def create_user(
        self,
        *,
        username: str,
        password: str,
        permission_ids: list[int],
        full_name: str | None = None,
        phone: str | None = None,
        email: str | None = None,
    ) -> User:
        user = User(
            username=username,
            password_hash=get_password_hash(password),
            is_active=True,
            full_name=full_name,
            phone=phone,
            email=email,
        )
        user.permissions = self.list_permissions_by_ids(permission_ids)

        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicateUserError("用户名已存在") from exc

        self.db.refresh(user)
        return user

    def update_user(
        self,
        *,
        user_id: int,
        full_name: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        is_active: bool | None = None,
    ) -> User:
        user = self.get_user(user_id)
        if not user:
            raise NotFoundError("用户不存在")

        user.full_name = full_name
        user.phone = phone
        user.email = email
        if is_active is not None:
            user.is_active = bool(is_active)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> None:
        user = self.get_user(user_id)
        if not user:
            raise NotFoundError("用户不存在")

        self.db.delete(user)
        self.db.commit()

    def reset_password(self, user_id: int, new_password: str) -> User:
        user = self.get_user(user_id)
        if not user:
            raise NotFoundError("用户不存在")

        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        self.db.refresh(user)
        return user

    def replace_permission_ids(self, user_id: int, permission_ids: set[int]) -> User:
        user = self.get_user(user_id)
        if not user:
            raise NotFoundError("用户不存在")

        self.db.execute(user_permissions.delete().where(user_permissions.c.user_id == int(user_id)))
        for permission_id in sorted(permission_ids):
            self.db.execute(
                user_permissions.insert().values(
                    user_id=int(user_id),
                    permission_id=int(permission_id),
                )
            )

        self.db.commit()
        self.db.refresh(user)
        return user


__all__ = ["UserRepository"]
