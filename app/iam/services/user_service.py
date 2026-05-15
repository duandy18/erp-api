from __future__ import annotations

from sqlalchemy.orm import Session

from app.iam.models.user import User
from app.iam.repositories.user_repository import UserRepository
from app.iam.services.user_auth_service import authenticate_user, issue_user_token
from app.iam.services.user_errors import AuthorizationError, DuplicateUserError, NotFoundError
from app.iam.services.user_permission_service import check_user_permission, get_user_permissions


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

    def list_users(self) -> list[User]:
        return self.repo.list_users()

    def get_user(self, user_id: int) -> User:
        user = self.repo.get_user(user_id)
        if not user:
            raise NotFoundError("用户不存在")
        return user

    def get_user_permissions(self, user: User) -> list[str]:
        return get_user_permissions(self.db, user)

    def check_permission(self, user: User, required: list[str]) -> None:
        check_user_permission(self.db, user, required)

    def login(self, username: str, password: str) -> tuple[User, str]:
        user = authenticate_user(self.db, username, password)
        if not user:
            raise AuthorizationError("用户名或密码错误")
        return user, issue_user_token(user)

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
        return self.repo.create_user(
            username=username,
            password=password,
            permission_ids=permission_ids,
            full_name=full_name,
            phone=phone,
            email=email,
        )

    def update_user(
        self,
        *,
        user_id: int,
        full_name: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        is_active: bool | None = None,
    ) -> User:
        return self.repo.update_user(
            user_id=user_id,
            full_name=full_name,
            phone=phone,
            email=email,
            is_active=is_active,
        )

    def delete_user(self, user_id: int) -> None:
        self.repo.delete_user(user_id)

    def reset_user_password(self, user_id: int, new_password: str) -> User:
        return self.repo.reset_password(user_id, new_password)


__all__ = [
    "AuthorizationError",
    "DuplicateUserError",
    "NotFoundError",
    "UserService",
]
