from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.deps import get_db
from app.iam.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.isdigit():
            raise ValueError("invalid token subject")
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="登录已失效") from exc

    user = db.query(User).filter(User.id == int(subject)).one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已停用")

    return user


__all__ = ["get_current_user", "oauth2_scheme"]
