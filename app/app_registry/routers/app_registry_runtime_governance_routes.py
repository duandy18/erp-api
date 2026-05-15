from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.app_registry.contracts.app_registry_runtime_governance_contracts import (
    AppRegistryHealthCheckRunOut,
)
from app.app_registry.repositories.app_registry_runtime_governance_repository import (
    AppRegistryRuntimeGovernanceSaveError,
)
from app.app_registry.services.app_registry_runtime_governance_service import (
    AppRegistryHealthCheckInactiveError,
    AppRegistryHealthCheckNotFoundError,
    AppRegistryHealthCheckUnsupportedError,
    AppRegistryRuntimeGovernanceService,
)
from app.db.deps import get_db
from app.iam.deps.auth import get_current_user
from app.iam.models.user import User
from app.iam.services.user_errors import AuthorizationError
from app.iam.services.user_service import UserService

router = APIRouter(prefix="/admin/app-registry", tags=["admin-app-registry"])

DBSessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]

ERP_SYSTEM_WRITE = "page.erp.system.write"


def _check_admin_write(svc: UserService, current_user: User) -> None:
    try:
        svc.check_permission(current_user, [ERP_SYSTEM_WRITE])
    except AuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post(
    "/health-checks/{health_check_id}/run",
    response_model=AppRegistryHealthCheckRunOut,
)
def run_app_registry_health_check(
    health_check_id: int,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> AppRegistryHealthCheckRunOut:
    user_svc = UserService(db)
    _check_admin_write(user_svc, current_user)

    try:
        return AppRegistryRuntimeGovernanceService(db).run_health_check_once(health_check_id)
    except AppRegistryHealthCheckNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (AppRegistryHealthCheckInactiveError, AppRegistryHealthCheckUnsupportedError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AppRegistryRuntimeGovernanceSaveError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


__all__ = ["router"]
