from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.iam.contracts.navigation import MyNavigationOut
from app.iam.contracts.user import UserMeOut
from app.iam.deps.auth import get_current_user
from app.iam.models.user import User
from app.iam.services.user_navigation_service import UserNavigationService
from app.iam.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

DBSessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get("/me", response_model=UserMeOut)
def get_me(
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> UserMeOut:
    permissions = UserService(db).get_user_permissions(current_user)
    return UserMeOut(
        id=int(current_user.id),
        username=str(current_user.username),
        permissions=permissions,
    )


@router.get("/me/navigation", response_model=MyNavigationOut)
def get_my_navigation(
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> MyNavigationOut:
    return UserNavigationService(db).get_navigation_for_user(current_user)


__all__ = ["router"]
