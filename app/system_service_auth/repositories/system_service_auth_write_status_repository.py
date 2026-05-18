from __future__ import annotations

from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryServiceClient,
    AppRegistryServicePermission,
    AppRegistryServicePermissionWriteRun,
)


class SystemServiceAuthWriteStatusRepository:
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

    def list_latest_write_runs(
        self,
        permission_ids: set[int],
    ) -> list[AppRegistryServicePermissionWriteRun]:
        if not permission_ids:
            return []

        return (
            self.db.query(AppRegistryServicePermissionWriteRun)
            .filter(AppRegistryServicePermissionWriteRun.permission_id.in_(permission_ids))
            .order_by(
                AppRegistryServicePermissionWriteRun.permission_id.asc(),
                AppRegistryServicePermissionWriteRun.started_at.desc(),
                AppRegistryServicePermissionWriteRun.id.desc(),
            )
            .all()
        )

    def list_recent_write_runs(
        self,
        *,
        limit: int = 100,
    ) -> list[AppRegistryServicePermissionWriteRun]:
        return (
            self.db.query(AppRegistryServicePermissionWriteRun)
            .order_by(
                AppRegistryServicePermissionWriteRun.started_at.desc(),
                AppRegistryServicePermissionWriteRun.id.desc(),
            )
            .limit(limit)
            .all()
        )


__all__ = ["SystemServiceAuthWriteStatusRepository"]
