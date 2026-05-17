from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.iam.deps.auth import get_current_user
from app.iam.models.user import User
from app.iam.services.user_errors import AuthorizationError
from app.iam.services.user_service import UserService
from app.system_monitoring.contracts.system_monitoring_database_contracts import (
    SystemMonitoringDatabaseStatusListOut,
)
from app.system_monitoring.services.system_monitoring_database_service import (
    SystemMonitoringDatabaseService,
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


@router.get("/databases", response_model=SystemMonitoringDatabaseStatusListOut)
def list_system_monitoring_database_statuses(
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> SystemMonitoringDatabaseStatusListOut:
    user_svc = UserService(db)
    _check_admin_read(user_svc, current_user)
    return SystemMonitoringDatabaseService(db).list_database_statuses()


__all__ = ["router"]
