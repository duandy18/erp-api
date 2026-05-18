from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.system_iam.contracts import (
    IndependentSystemUserPermissionsOut,
    SystemIamAppOut,
    SystemIamPageOut,
    SystemIamPageRoutePrefixOut,
    SystemIamPermissionOut,
    SystemIamSyncRunOut,
    SystemIamUserOut,
    SystemIamUserPermissionOut,
)
from app.system_iam.repositories import SystemIamProjectionRepository


def _int_value(value: Any) -> int:
    return int(value)


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def _bool_value(value: Any) -> bool:
    return bool(value)


class IndependentSystemUserPermissionsService:
    def __init__(
        self,
        db: Session,
        *,
        repository: SystemIamProjectionRepository | None = None,
    ) -> None:
        self.repo = repository or SystemIamProjectionRepository(db)

    def list_independent_system_user_permissions(
        self,
        *,
        app_code: str | None = None,
    ) -> IndependentSystemUserPermissionsOut:
        normalized_app_code = app_code.strip() if app_code and app_code.strip() else None
        apps = self.repo.list_apps(normalized_app_code)
        app_codes = [str(row.code) for row in apps]

        return IndependentSystemUserPermissionsOut(
            apps=[self._app_out(row) for row in apps],
            users=[self._user_out(row) for row in self.repo.list_users(app_codes)],
            permissions=[
                self._permission_out(row)
                for row in self.repo.list_permissions(app_codes)
            ],
            user_permissions=[
                self._user_permission_out(row)
                for row in self.repo.list_user_permissions(app_codes)
            ],
            page_registry=[
                self._page_out(row)
                for row in self.repo.list_pages(app_codes)
            ],
            page_route_prefixes=[
                self._route_prefix_out(row)
                for row in self.repo.list_route_prefixes(app_codes)
            ],
            latest_sync_runs=[
                self._sync_run_out(row)
                for row in self.repo.list_latest_sync_runs(app_codes)
            ],
        )

    @staticmethod
    def _app_out(row: Any) -> SystemIamAppOut:
        return SystemIamAppOut(
            app_code=str(row.code),
            app_name=str(row.name),
            app_type=str(row.app_type),
            status=str(row.status),
            is_active=_bool_value(row.is_active),
        )

    @staticmethod
    def _sync_run_out(row: Any) -> SystemIamSyncRunOut:
        return SystemIamSyncRunOut(
            id=_int_value(row.id),
            app_code=str(row.app_code),
            source_base_url=str(row.source_base_url),
            status=str(row.status),
            started_at=row.started_at,
            finished_at=row.finished_at,
            source_snapshot_at=row.source_snapshot_at,
            fetched_count=_int_value(row.fetched_count),
            inserted_count=_int_value(row.inserted_count),
            updated_count=_int_value(row.updated_count),
            deleted_count=_int_value(row.deleted_count),
            error_message=row.error_message,
            raw_excerpt=row.raw_excerpt,
        )

    @staticmethod
    def _user_out(row: Any) -> SystemIamUserOut:
        return SystemIamUserOut(
            app_code=str(row.app_code),
            source_user_id=_int_value(row.source_user_id),
            username=str(row.username),
            is_active=_bool_value(row.is_active),
            full_name=row.full_name,
            phone=row.phone,
            email=row.email,
            last_synced_at=row.last_synced_at,
        )

    @staticmethod
    def _permission_out(row: Any) -> SystemIamPermissionOut:
        return SystemIamPermissionOut(
            app_code=str(row.app_code),
            source_permission_id=_int_value(row.source_permission_id),
            permission_code=str(row.permission_code),
            last_synced_at=row.last_synced_at,
        )

    @staticmethod
    def _user_permission_out(row: Any) -> SystemIamUserPermissionOut:
        return SystemIamUserPermissionOut(
            app_code=str(row.app_code),
            source_user_id=_int_value(row.source_user_id),
            source_permission_id=_int_value(row.source_permission_id),
            permission_code=str(row.permission_code),
            granted_at=row.granted_at,
            last_synced_at=row.last_synced_at,
        )

    @staticmethod
    def _page_out(row: Any) -> SystemIamPageOut:
        return SystemIamPageOut(
            app_code=str(row.app_code),
            page_code=str(row.page_code),
            page_name=str(row.page_name),
            parent_page_code=row.parent_page_code,
            level=_int_value(row.level),
            domain_code=row.domain_code,
            show_in_topbar=_bool_value(row.show_in_topbar),
            show_in_sidebar=_bool_value(row.show_in_sidebar),
            inherit_permissions=_bool_value(row.inherit_permissions),
            read_permission_code=row.read_permission_code,
            write_permission_code=row.write_permission_code,
            sort_order=_optional_int(row.sort_order),
            is_active=row.is_active,
            last_synced_at=row.last_synced_at,
        )

    @staticmethod
    def _route_prefix_out(row: Any) -> SystemIamPageRoutePrefixOut:
        return SystemIamPageRoutePrefixOut(
            app_code=str(row.app_code),
            page_code=str(row.page_code),
            route_prefix=str(row.route_prefix),
            sort_order=_optional_int(row.sort_order),
            is_active=row.is_active,
            last_synced_at=row.last_synced_at,
        )


__all__ = ["IndependentSystemUserPermissionsService"]
