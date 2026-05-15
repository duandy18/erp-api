from __future__ import annotations

from sqlalchemy.orm import Session

from app.iam.models.user import User
from app.iam.repositories.user_repository import UserRepository
from app.iam.services.user_auth_service import authenticate_user, issue_user_token
from app.iam.services.user_errors import AuthorizationError, NotFoundError
from app.iam.services.user_permission_service import check_user_permission, get_user_permissions


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

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


__all__ = ["AuthorizationError", "NotFoundError", "UserService"]
