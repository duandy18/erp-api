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
from app.system_service_auth.contracts.system_service_auth_permission_contracts import (
    SystemServiceAuthPermissionCreateIn,
    SystemServiceAuthPermissionListOut,
    SystemServiceAuthPermissionOut,
    SystemServiceAuthPermissionUpdateIn,
)
from app.system_service_auth.repositories.system_service_auth_permission_repository import (
    DuplicateSystemServiceAuthPermissionError,
    SystemServiceAuthPermissionSaveError,
)
from app.system_service_auth.services.system_service_auth_capability_service import (
    SystemServiceAuthCapabilityService,
)
from app.system_service_auth.services.system_service_auth_permission_service import (
    SystemServiceAuthCapabilityNotFoundError,
    SystemServiceAuthClientNotFoundError,
    SystemServiceAuthPermissionNotFoundError,
    SystemServiceAuthPermissionService,
    SystemServiceAuthPermissionValidationError,
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


def _check_admin_write(svc: UserService, current_user: User) -> None:
    try:
        svc.check_permission(current_user, [ERP_SYSTEM_WRITE])
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


@router.get("/permissions", response_model=SystemServiceAuthPermissionListOut)
def list_system_service_auth_permissions(
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> SystemServiceAuthPermissionListOut:
    user_svc = UserService(db)
    _check_admin_read(user_svc, current_user)

    return SystemServiceAuthPermissionService(db).list_permissions()


@router.post(
    "/permissions",
    response_model=SystemServiceAuthPermissionOut,
    status_code=201,
)
def create_system_service_auth_permission(
    body: SystemServiceAuthPermissionCreateIn,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> SystemServiceAuthPermissionOut:
    user_svc = UserService(db)
    _check_admin_write(user_svc, current_user)

    try:
        return SystemServiceAuthPermissionService(db).create_permission(body)
    except (
        SystemServiceAuthClientNotFoundError,
        SystemServiceAuthCapabilityNotFoundError,
    ) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DuplicateSystemServiceAuthPermissionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except SystemServiceAuthPermissionValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SystemServiceAuthPermissionSaveError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.patch(
    "/permissions/{permission_id}",
    response_model=SystemServiceAuthPermissionOut,
)
def update_system_service_auth_permission(
    permission_id: int,
    body: SystemServiceAuthPermissionUpdateIn,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> SystemServiceAuthPermissionOut:
    user_svc = UserService(db)
    _check_admin_write(user_svc, current_user)

    try:
        return SystemServiceAuthPermissionService(db).update_permission(permission_id, body)
    except SystemServiceAuthPermissionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SystemServiceAuthPermissionValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SystemServiceAuthPermissionSaveError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


__all__ = ["router"]
