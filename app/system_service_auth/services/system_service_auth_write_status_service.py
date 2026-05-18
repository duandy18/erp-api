from __future__ import annotations

from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryServiceClient,
    AppRegistryServicePermission,
    AppRegistryServicePermissionWriteRun,
)
from app.system_service_auth.contracts.system_service_auth_write_status_contracts import (
    SystemServiceAuthWriteRunOut,
    SystemServiceAuthWriteStatusItemOut,
    SystemServiceAuthWriteStatusListOut,
)
from app.system_service_auth.repositories.system_service_auth_write_status_repository import (
    SystemServiceAuthWriteStatusRepository,
)


def _app_name(app_by_code: dict[str, AppRegistryApp], app_code: object) -> str:
    code = str(app_code)
    row = app_by_code.get(code)
    return str(row.name) if row is not None else code


class SystemServiceAuthWriteStatusService:
    def __init__(
        self,
        db: Session,
        *,
        repository: SystemServiceAuthWriteStatusRepository | None = None,
    ) -> None:
        self.repo = repository or SystemServiceAuthWriteStatusRepository(db)

    def list_write_status(self) -> SystemServiceAuthWriteStatusListOut:
        apps = self.repo.list_apps()
        clients = self.repo.list_clients()
        permissions = self.repo.list_permissions()
        latest_runs = self.repo.list_latest_write_runs({int(row.id) for row in permissions})
        recent_runs = self.repo.list_recent_write_runs()

        app_by_code = {str(row.code): row for row in apps}
        client_by_id = {int(row.id): row for row in clients}
        latest_run_by_permission_id: dict[int, AppRegistryServicePermissionWriteRun] = {}

        for row in latest_runs:
            permission_id = int(row.permission_id)
            if permission_id not in latest_run_by_permission_id:
                latest_run_by_permission_id[permission_id] = row

        return SystemServiceAuthWriteStatusListOut(
            items=[
                self._item_out(
                    row=row,
                    app_by_code=app_by_code,
                    client_by_id=client_by_id,
                    latest_run=latest_run_by_permission_id.get(int(row.id)),
                )
                for row in permissions
            ],
            recent_runs=[self._run_out(row) for row in recent_runs],
        )

    @classmethod
    def _item_out(
        cls,
        *,
        row: AppRegistryServicePermission,
        app_by_code: dict[str, AppRegistryApp],
        client_by_id: dict[int, AppRegistryServiceClient],
        latest_run: AppRegistryServicePermissionWriteRun | None,
    ) -> SystemServiceAuthWriteStatusItemOut:
        client = client_by_id.get(int(row.client_id))

        return SystemServiceAuthWriteStatusItemOut(
            permission_id=int(row.id),
            client_id=int(row.client_id),
            client_code=str(client.client_code) if client is not None else None,
            source_app_code=str(row.source_app_code),
            source_app_name=_app_name(app_by_code, row.source_app_code),
            target_app_code=str(row.target_app_code),
            target_app_name=_app_name(app_by_code, row.target_app_code),
            permission_code=str(row.permission_code),
            description=str(row.description),
            permission_active=bool(row.is_active),
            latest_run=cls._run_out(latest_run) if latest_run is not None else None,
        )

    @staticmethod
    def _run_out(row: AppRegistryServicePermissionWriteRun) -> SystemServiceAuthWriteRunOut:
        return SystemServiceAuthWriteRunOut(
            run_id=int(row.id),
            permission_id=int(row.permission_id),
            source_app_code=str(row.source_app_code),
            target_app_code=str(row.target_app_code),
            client_code=row.client_code,
            permission_code=str(row.permission_code),
            operation=str(row.operation),
            status=str(row.status),
            started_at=row.started_at,
            finished_at=row.finished_at,
            target_base_url=row.target_base_url,
            http_status=row.http_status,
            error_message=row.error_message,
            raw_excerpt=row.raw_excerpt,
        )


__all__ = ["SystemServiceAuthWriteStatusService"]
