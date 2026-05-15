from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.app_registry.contracts.app_registry_contracts import AppRegistryAppsOut
from app.app_registry.services.app_registry_service import AppRegistryService
from app.db.deps import get_db
from app.iam.deps.auth import get_current_user
from app.iam.models.user import User
from app.iam.services.user_errors import AuthorizationError
from app.iam.services.user_service import UserService

router = APIRouter(prefix="/erp/app-registry", tags=["erp-app-registry"])

DBSessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]

ERP_APPS_READ = "page.erp.apps.read"
ERP_APPS_WRITE = "page.erp.apps.write"


@router.get("/apps", response_model=AppRegistryAppsOut)
def list_registered_apps(
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> AppRegistryAppsOut:
    svc = UserService(db)
    try:
        svc.check_permission(current_user, [ERP_APPS_READ, ERP_APPS_WRITE])
    except AuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return AppRegistryService(db).list_apps()


__all__ = ["router"]
