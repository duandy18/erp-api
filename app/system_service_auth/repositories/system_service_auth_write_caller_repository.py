from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryServiceClient,
    AppRegistryServicePermission,
)


class SystemServiceAuthWriteSaveError(ValueError):
    pass


class SystemServiceAuthWriteCallerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_permission(self, permission_id: int) -> AppRegistryServicePermission | None:
        return (
            self.db.query(AppRegistryServicePermission)
            .filter(AppRegistryServicePermission.id == int(permission_id))
            .one_or_none()
        )

    def get_client(self, client_id: int) -> AppRegistryServiceClient | None:
        return (
            self.db.query(AppRegistryServiceClient)
            .filter(AppRegistryServiceClient.id == int(client_id))
            .one_or_none()
        )

    def get_app(self, app_code: str) -> AppRegistryApp | None:
        return (
            self.db.query(AppRegistryApp)
            .filter(AppRegistryApp.code == app_code)
            .one_or_none()
        )

    def add(self, row: object) -> None:
        self.db.add(row)

    def flush(self) -> None:
        try:
            self.db.flush()
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise SystemServiceAuthWriteSaveError("系统调用授权写入记录创建失败") from exc

    def commit(self) -> None:
        try:
            self.db.commit()
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise SystemServiceAuthWriteSaveError("系统调用授权写入记录保存失败") from exc

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, row: object) -> None:
        self.db.refresh(row)


__all__ = [
    "SystemServiceAuthWriteCallerRepository",
    "SystemServiceAuthWriteSaveError",
]
