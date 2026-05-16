from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.app_registry.contracts.app_registry_app_metadata_contracts import (
    AppRegistryAppMetadataListOut,
    AppRegistryAppMetadataOut,
)
from app.app_registry.services.app_registry_app_metadata_service import (
    AppRegistryAppMetadataNotFoundError,
    AppRegistryAppMetadataService,
)
from app.db.deps import get_db
from app.iam.deps.auth import get_current_user
from app.iam.models.user import User
from app.iam.services.user_errors import AuthorizationError
from app.iam.services.user_service import UserService

router = APIRouter(prefix="/admin/app-registry", tags=["admin-app-registry"])

DBSessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]

ERP_SYSTEM_READ = "page.erp.system.read"
ERP_SYSTEM_WRITE = "page.erp.system.write"


def _check_admin_read(svc: UserService, current_user: User) -> None:
    try:
        svc.check_permission(current_user, [ERP_SYSTEM_READ, ERP_SYSTEM_WRITE])
    except AuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/app-metadata", response_model=AppRegistryAppMetadataListOut)
def list_app_metadatas(
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> AppRegistryAppMetadataListOut:
    user_svc = UserService(db)
    _check_admin_read(user_svc, current_user)
    return AppRegistryAppMetadataService(db).list_profiles()


@router.get("/app-metadata/{app_code}", response_model=AppRegistryAppMetadataOut)
def get_app_metadata(
    app_code: str,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> AppRegistryAppMetadataOut:
    user_svc = UserService(db)
    _check_admin_read(user_svc, current_user)

    try:
        return AppRegistryAppMetadataService(db).get_profile(app_code)
    except AppRegistryAppMetadataNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


__all__ = ["router"]
