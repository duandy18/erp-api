from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.app_registry.contracts.app_registry_admin_contracts import (
    AppRegistryAdminAppCreateIn,
    AppRegistryAdminAppsOut,
    AppRegistryAdminAppUpdateIn,
)
from app.app_registry.contracts.app_registry_contracts import AppRegistryAppOut
from app.app_registry.contracts.app_registry_self_description_sync_contracts import (
    AppRegistrySelfDescriptionSyncRunOut,
)
from app.app_registry.repositories.app_registry_self_description_sync_repository import (
    AppRegistrySelfDescriptionSyncSaveError,
)
from app.app_registry.services.app_registry_admin_service import (
    AppRegistryAdminService,
    AppRegistryAppNotFoundError,
    AppRegistryAppSaveError,
    DuplicateAppRegistryAppError,
)
from app.app_registry.services.app_registry_self_description_sync_service import (
    AppRegistrySelfDescriptionAppNotFoundError,
    AppRegistrySelfDescriptionFetchError,
    AppRegistrySelfDescriptionPayloadError,
    AppRegistrySelfDescriptionSyncService,
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


def _check_admin_write(svc: UserService, current_user: User) -> None:
    try:
        svc.check_permission(current_user, [ERP_SYSTEM_WRITE])
    except AuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/apps", response_model=AppRegistryAdminAppsOut)
def list_admin_registered_apps(
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> AppRegistryAdminAppsOut:
    user_svc = UserService(db)
    _check_admin_read(user_svc, current_user)
    return AppRegistryAdminService(db).list_apps()


@router.post("/apps", response_model=AppRegistryAppOut, status_code=201)
def create_admin_registered_app(
    body: AppRegistryAdminAppCreateIn,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> AppRegistryAppOut:
    user_svc = UserService(db)
    _check_admin_write(user_svc, current_user)

    try:
        return AppRegistryAdminService(db).create_app(body)
    except DuplicateAppRegistryAppError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except AppRegistryAppSaveError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/apps/{code}", response_model=AppRegistryAppOut)
def update_admin_registered_app(
    code: str,
    body: AppRegistryAdminAppUpdateIn,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> AppRegistryAppOut:
    user_svc = UserService(db)
    _check_admin_write(user_svc, current_user)

    try:
        return AppRegistryAdminService(db).update_app(code=code, body=body)
    except AppRegistryAppNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AppRegistryAppSaveError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/apps/{code}/sync-self-description",
    response_model=AppRegistrySelfDescriptionSyncRunOut,
)
def sync_admin_app_self_description(
    code: str,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> AppRegistrySelfDescriptionSyncRunOut:
    user_svc = UserService(db)
    _check_admin_write(user_svc, current_user)

    try:
        return AppRegistrySelfDescriptionSyncService(db).sync_app_self_description(code)
    except AppRegistrySelfDescriptionAppNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (
        AppRegistrySelfDescriptionFetchError,
        AppRegistrySelfDescriptionPayloadError,
    ) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except AppRegistrySelfDescriptionSyncSaveError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/apps/{code}/enable", response_model=AppRegistryAppOut)
def enable_admin_registered_app(
    code: str,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> AppRegistryAppOut:
    user_svc = UserService(db)
    _check_admin_write(user_svc, current_user)

    try:
        return AppRegistryAdminService(db).enable_app(code)
    except AppRegistryAppNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AppRegistryAppSaveError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/apps/{code}/disable", response_model=AppRegistryAppOut)
def disable_admin_registered_app(
    code: str,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> AppRegistryAppOut:
    user_svc = UserService(db)
    _check_admin_write(user_svc, current_user)

    try:
        return AppRegistryAdminService(db).disable_app(code)
    except AppRegistryAppNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AppRegistryAppSaveError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


__all__ = ["router"]
