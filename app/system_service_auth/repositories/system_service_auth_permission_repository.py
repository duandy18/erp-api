from __future__ import annotations

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryServiceClient,
    AppRegistryServicePermission,
)
from app.app_registry.models.app_registry_self_description_projection import (
    AppRegistryServiceCapabilityCatalog,
)


class SystemServiceAuthPermissionSaveError(ValueError):
    pass


class DuplicateSystemServiceAuthPermissionError(ValueError):
    pass


class SystemServiceAuthPermissionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_apps(self) -> list[AppRegistryApp]:
        return (
            self.db.query(AppRegistryApp)
            .order_by(AppRegistryApp.sort_order.asc(), AppRegistryApp.code.asc())
            .all()
        )

    def list_clients(self) -> list[AppRegistryServiceClient]:
        return (
            self.db.query(AppRegistryServiceClient)
            .order_by(
                AppRegistryServiceClient.app_code.asc(),
                AppRegistryServiceClient.client_code.asc(),
            )
            .all()
        )

    def get_client(self, client_id: int) -> AppRegistryServiceClient | None:
        return (
            self.db.query(AppRegistryServiceClient)
            .filter(AppRegistryServiceClient.id == int(client_id))
            .one_or_none()
        )

    def list_capability_options(self) -> list[AppRegistryServiceCapabilityCatalog]:
        return (
            self.db.query(AppRegistryServiceCapabilityCatalog)
            .order_by(
                AppRegistryServiceCapabilityCatalog.app_code.asc(),
                AppRegistryServiceCapabilityCatalog.capability_code.asc(),
            )
            .all()
        )

    def get_capability_by_permission(
        self,
        *,
        target_app_code: str,
        permission_code: str,
    ) -> AppRegistryServiceCapabilityCatalog | None:
        return (
            self.db.query(AppRegistryServiceCapabilityCatalog)
            .filter(
                AppRegistryServiceCapabilityCatalog.app_code == target_app_code,
                AppRegistryServiceCapabilityCatalog.permission_code == permission_code,
            )
            .one_or_none()
        )

    def list_permissions(self) -> list[AppRegistryServicePermission]:
        return (
            self.db.query(AppRegistryServicePermission)
            .order_by(
                AppRegistryServicePermission.source_app_code.asc(),
                AppRegistryServicePermission.target_app_code.asc(),
                AppRegistryServicePermission.permission_code.asc(),
            )
            .all()
        )

    def get_permission(self, permission_id: int) -> AppRegistryServicePermission | None:
        return (
            self.db.query(AppRegistryServicePermission)
            .filter(AppRegistryServicePermission.id == int(permission_id))
            .one_or_none()
        )

    def find_permission(
        self,
        *,
        client_id: int,
        permission_code: str,
    ) -> AppRegistryServicePermission | None:
        return (
            self.db.query(AppRegistryServicePermission)
            .filter(
                AppRegistryServicePermission.client_id == int(client_id),
                AppRegistryServicePermission.permission_code == permission_code,
            )
            .one_or_none()
        )

    def save_permission(
        self,
        row: AppRegistryServicePermission,
    ) -> AppRegistryServicePermission:
        self.db.add(row)

        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicateSystemServiceAuthPermissionError("该 client 已存在相同授权") from exc
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise SystemServiceAuthPermissionSaveError("系统调用授权保存失败") from exc

        self.db.refresh(row)
        return row


__all__ = [
    "DuplicateSystemServiceAuthPermissionError",
    "SystemServiceAuthPermissionRepository",
    "SystemServiceAuthPermissionSaveError",
]
