from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.iam.deps.auth import get_current_user
from app.iam.models.user import User
from app.iam.services.user_errors import AuthorizationError
from app.iam.services.user_service import UserService
from app.system_iam.contracts import IndependentSystemUserPermissionsOut
from app.system_iam.services import IndependentSystemUserPermissionsService

router = APIRouter(prefix="/admin/system-iam", tags=["admin-system-iam"])

DBSessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]

ERP_SYSTEM_READ = "page.erp.system.read"
ERP_SYSTEM_WRITE = "page.erp.system.write"


def _check_admin_read(svc: UserService, current_user: User) -> None:
    try:
        svc.check_permission(current_user, [ERP_SYSTEM_READ, ERP_SYSTEM_WRITE])
    except AuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get(
    "/independent-system-user-permissions",
    response_model=IndependentSystemUserPermissionsOut,
)
def list_independent_system_user_permissions(
    db: DBSessionDep,
    current_user: CurrentUserDep,
    app_code: str | None = Query(default=None, min_length=1),
) -> IndependentSystemUserPermissionsOut:
    user_svc = UserService(db)
    _check_admin_read(user_svc, current_user)

    return IndependentSystemUserPermissionsService(
        db,
    ).list_independent_system_user_permissions(app_code=app_code)


__all__ = ["router"]
