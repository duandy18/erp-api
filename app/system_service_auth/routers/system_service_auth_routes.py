from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.iam.deps.auth import get_current_user
from app.iam.models.user import User
from app.iam.services.user_errors import AuthorizationError
from app.iam.services.user_service import UserService
from app.system_service_auth.contracts.system_service_auth_capability_contracts import (
    SystemServiceAuthCapabilityListOut,
)
from app.system_service_auth.services.system_service_auth_capability_service import (
    SystemServiceAuthCapabilityService,
)

router = APIRouter(prefix="/admin/system-service-auth", tags=["admin-system-service-auth"])

DBSessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]

ERP_SYSTEM_READ = "page.erp.system.read"
ERP_SYSTEM_WRITE = "page.erp.system.write"


def _check_admin_read(svc: UserService, current_user: User) -> None:
    try:
        svc.check_permission(current_user, [ERP_SYSTEM_READ, ERP_SYSTEM_WRITE])
    except AuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/capabilities", response_model=SystemServiceAuthCapabilityListOut)
def list_system_service_auth_capabilities(
    db: DBSessionDep,
    current_user: CurrentUserDep,
    target_app_code: Annotated[str | None, Query()] = None,
) -> SystemServiceAuthCapabilityListOut:
    user_svc = UserService(db)
    _check_admin_read(user_svc, current_user)

    return SystemServiceAuthCapabilityService(db).list_capabilities(
        target_app_code=target_app_code
    )


__all__ = ["router"]
