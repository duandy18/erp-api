from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_iam_projection import (
    AppRegistryIamPageProjection,
    AppRegistryIamPageRoutePrefixProjection,
    AppRegistryIamPermissionProjection,
    AppRegistryIamUserPermissionProjection,
    AppRegistryIamUserProjection,
)


class SystemIamSnapshotSyncSaveError(ValueError):
    pass


class SystemIamSnapshotSyncRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_app(self, code: str) -> AppRegistryApp | None:
        return (
            self.db.query(AppRegistryApp)
            .filter(AppRegistryApp.code == code)
            .one_or_none()
        )

    def list_users(self, app_code: str) -> list[AppRegistryIamUserProjection]:
        return (
            self.db.query(AppRegistryIamUserProjection)
            .filter(AppRegistryIamUserProjection.app_code == app_code)
            .all()
        )

    def list_permissions(self, app_code: str) -> list[AppRegistryIamPermissionProjection]:
        return (
            self.db.query(AppRegistryIamPermissionProjection)
            .filter(AppRegistryIamPermissionProjection.app_code == app_code)
            .all()
        )

    def list_user_permissions(
        self,
        app_code: str,
    ) -> list[AppRegistryIamUserPermissionProjection]:
        return (
            self.db.query(AppRegistryIamUserPermissionProjection)
            .filter(AppRegistryIamUserPermissionProjection.app_code == app_code)
            .all()
        )

    def list_pages(self, app_code: str) -> list[AppRegistryIamPageProjection]:
        return (
            self.db.query(AppRegistryIamPageProjection)
            .filter(AppRegistryIamPageProjection.app_code == app_code)
            .all()
        )

    def list_route_prefixes(
        self,
        app_code: str,
    ) -> list[AppRegistryIamPageRoutePrefixProjection]:
        return (
            self.db.query(AppRegistryIamPageRoutePrefixProjection)
            .filter(AppRegistryIamPageRoutePrefixProjection.app_code == app_code)
            .all()
        )

    def add(self, row: object) -> None:
        self.db.add(row)

    def delete(self, row: object) -> None:
        self.db.delete(row)

    def flush(self) -> None:
        try:
            self.db.flush()
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise SystemIamSnapshotSyncSaveError("IAM 快照同步数据写入失败") from exc

    def commit(self) -> None:
        try:
            self.db.commit()
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise SystemIamSnapshotSyncSaveError("IAM 快照同步数据保存失败") from exc

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, row: object) -> None:
        self.db.refresh(row)


__all__ = [
    "SystemIamSnapshotSyncRepository",
    "SystemIamSnapshotSyncSaveError",
]
