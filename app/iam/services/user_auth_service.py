from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.iam.models.user import User


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).one_or_none()
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def issue_user_token(user: User) -> str:
    return create_access_token(str(user.id))


__all__ = ["authenticate_user", "issue_user_token"]
