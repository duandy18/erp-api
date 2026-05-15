from __future__ import annotations

from sqlalchemy.orm import Session

from app.iam.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == int(user_id)).one_or_none()

    def get_user_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).one_or_none()


__all__ = ["UserRepository"]
