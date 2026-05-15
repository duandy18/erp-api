from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.deps import get_db
from app.iam.contracts.auth import TokenOut, UserLoginIn
from app.iam.services.user_errors import AuthorizationError
from app.iam.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

DBSessionDep = Annotated[Session, Depends(get_db)]


@router.post("/login", response_model=TokenOut)
def login(body: UserLoginIn, db: DBSessionDep) -> TokenOut:
    try:
        _user, token = UserService(db).login(body.username, body.password)
    except AuthorizationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    return TokenOut(
        access_token=token,
        token_type="bearer",
        expires_in=get_settings().access_token_expire_seconds,
    )


__all__ = ["router"]
