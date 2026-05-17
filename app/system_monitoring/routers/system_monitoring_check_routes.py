from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.iam.deps.auth import get_current_user
from app.iam.models.user import User
from app.iam.services.user_errors import AuthorizationError
from app.iam.services.user_service import UserService
from app.system_monitoring.contracts.system_monitoring_check_contracts import (
    SystemMonitoringCheckResultOut,
)
from app.system_monitoring.services.system_monitoring_check_service import (
    SystemMonitoringCheckNotFoundError,
    SystemMonitoringCheckService,
    SystemMonitoringOpenApiSaveError,
)

router = APIRouter(prefix="/admin/system-monitoring", tags=["admin-system-monitoring"])

DBSessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]

ERP_SYSTEM_WRITE = "page.erp.system.write"


def _check_admin_write(svc: UserService, current_user: User) -> None:
    try:
        svc.check_permission(current_user, [ERP_SYSTEM_WRITE])
    except AuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("/gateway/{binding_id}/check", response_model=SystemMonitoringCheckResultOut)
def check_system_monitoring_gateway_binding(
    binding_id: int,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> SystemMonitoringCheckResultOut:
    user_svc = UserService(db)
    _check_admin_write(user_svc, current_user)
    try:
        return SystemMonitoringCheckService(db).check_gateway_binding(binding_id)
    except SystemMonitoringCheckNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/dependencies/{dependency_id}/check", response_model=SystemMonitoringCheckResultOut)
def check_system_monitoring_dependency(
    dependency_id: int,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> SystemMonitoringCheckResultOut:
    user_svc = UserService(db)
    _check_admin_write(user_svc, current_user)
    try:
        return SystemMonitoringCheckService(db).check_dependency(dependency_id)
    except SystemMonitoringCheckNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/service-auth/clients/{client_id}/check",
    response_model=SystemMonitoringCheckResultOut,
)
def check_system_monitoring_service_client(
    client_id: int,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> SystemMonitoringCheckResultOut:
    user_svc = UserService(db)
    _check_admin_write(user_svc, current_user)
    try:
        return SystemMonitoringCheckService(db).check_service_client(client_id)
    except SystemMonitoringCheckNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/service-auth/permissions/{permission_id}/check",
    response_model=SystemMonitoringCheckResultOut,
)
def check_system_monitoring_service_permission(
    permission_id: int,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> SystemMonitoringCheckResultOut:
    user_svc = UserService(db)
    _check_admin_write(user_svc, current_user)
    try:
        return SystemMonitoringCheckService(db).check_service_permission(permission_id)
    except SystemMonitoringCheckNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/openapi/{source_id}/check", response_model=SystemMonitoringCheckResultOut)
def check_system_monitoring_openapi_source(
    source_id: int,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> SystemMonitoringCheckResultOut:
    user_svc = UserService(db)
    _check_admin_write(user_svc, current_user)
    try:
        return SystemMonitoringCheckService(db).check_openapi_source(source_id)
    except SystemMonitoringCheckNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SystemMonitoringOpenApiSaveError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


__all__ = ["router"]
