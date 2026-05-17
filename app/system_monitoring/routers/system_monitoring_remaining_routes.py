from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.iam.deps.auth import get_current_user
from app.iam.models.user import User
from app.iam.services.user_errors import AuthorizationError
from app.iam.services.user_service import UserService
from app.system_monitoring.contracts.system_monitoring_remaining_contracts import (
    SystemMonitoringDependencyListOut,
    SystemMonitoringGatewayBindingListOut,
    SystemMonitoringHealthCheckListOut,
    SystemMonitoringOpenApiSourceListOut,
    SystemMonitoringServiceAuthOut,
)
from app.system_monitoring.services.system_monitoring_remaining_service import (
    SystemMonitoringRemainingService,
)

router = APIRouter(prefix="/admin/system-monitoring", tags=["admin-system-monitoring"])

DBSessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]

ERP_SYSTEM_READ = "page.erp.system.read"
ERP_SYSTEM_WRITE = "page.erp.system.write"


def _check_admin_read(svc: UserService, current_user: User) -> None:
    try:
        svc.check_permission(current_user, [ERP_SYSTEM_READ, ERP_SYSTEM_WRITE])
    except AuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/gateway", response_model=SystemMonitoringGatewayBindingListOut)
def list_system_monitoring_gateway_statuses(
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> SystemMonitoringGatewayBindingListOut:
    user_svc = UserService(db)
    _check_admin_read(user_svc, current_user)
    return SystemMonitoringRemainingService(db).list_gateway_bindings()


@router.get("/dependencies", response_model=SystemMonitoringDependencyListOut)
def list_system_monitoring_dependency_statuses(
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> SystemMonitoringDependencyListOut:
    user_svc = UserService(db)
    _check_admin_read(user_svc, current_user)
    return SystemMonitoringRemainingService(db).list_dependencies()


@router.get("/service-auth", response_model=SystemMonitoringServiceAuthOut)
def list_system_monitoring_service_auth_statuses(
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> SystemMonitoringServiceAuthOut:
    user_svc = UserService(db)
    _check_admin_read(user_svc, current_user)
    return SystemMonitoringRemainingService(db).list_service_auth()


@router.get("/openapi", response_model=SystemMonitoringOpenApiSourceListOut)
def list_system_monitoring_openapi_statuses(
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> SystemMonitoringOpenApiSourceListOut:
    user_svc = UserService(db)
    _check_admin_read(user_svc, current_user)
    return SystemMonitoringRemainingService(db).list_openapi_sources()


@router.get("/health", response_model=SystemMonitoringHealthCheckListOut)
def list_system_monitoring_health_check_statuses(
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> SystemMonitoringHealthCheckListOut:
    user_svc = UserService(db)
    _check_admin_read(user_svc, current_user)
    return SystemMonitoringRemainingService(db).list_health_checks()


__all__ = ["router"]
