from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.app_registry.contracts.app_registry_admin_contracts import (
    AppRegistryAdminAppCreateIn,
    AppRegistryAdminAppsOut,
    AppRegistryAdminAppUpdateIn,
)
from app.app_registry.contracts.app_registry_contracts import AppRegistryAppOut
from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.repositories.app_registry_admin_repository import (
    AppRegistryAdminRepository,
)


class AppRegistryAppNotFoundError(ValueError):
    pass


class DuplicateAppRegistryAppError(ValueError):
    pass


class AppRegistryAppSaveError(ValueError):
    pass


def _to_app_out(row: AppRegistryApp) -> AppRegistryAppOut:
    return AppRegistryAppOut(
        code=str(row.code),
        name=str(row.name),
        description=str(row.description),
        web_path=str(row.web_path),
        api_path=str(row.api_path),
        local_web_url=str(row.local_web_url),
        local_api_url=str(row.local_api_url),
        status=str(row.status),
        sort_order=int(row.sort_order),
        is_active=bool(row.is_active),
    )


class AppRegistryAdminService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AppRegistryAdminRepository(db)

    def list_apps(self) -> AppRegistryAdminAppsOut:
        return AppRegistryAdminAppsOut(
            apps=[_to_app_out(row) for row in self.repo.list_apps()]
        )

    def create_app(self, body: AppRegistryAdminAppCreateIn) -> AppRegistryAppOut:
        if self.repo.get_app(body.code) is not None:
            raise DuplicateAppRegistryAppError("应用编码已存在")

        row = AppRegistryApp(
            code=body.code,
            name=body.name,
            description=body.description,
            web_path=body.web_path,
            api_path=body.api_path,
            local_web_url=body.local_web_url,
            local_api_url=body.local_api_url,
            status=body.status,
            sort_order=body.sort_order,
            is_active=body.is_active,
        )
        self.repo.add_app(row)
        self._commit_and_refresh(row)
        return _to_app_out(row)

    def update_app(
        self,
        code: str,
        body: AppRegistryAdminAppUpdateIn,
    ) -> AppRegistryAppOut:
        row = self._get_required_app(code)
        updates = body.model_dump(exclude_unset=True)

        if not updates:
            return _to_app_out(row)

        for field_name, value in updates.items():
            if value is not None:
                setattr(row, field_name, value)

        row.updated_at = datetime.now(UTC)
        self._commit_and_refresh(row)
        return _to_app_out(row)

    def enable_app(self, code: str) -> AppRegistryAppOut:
        return self._set_active(code, is_active=True)

    def disable_app(self, code: str) -> AppRegistryAppOut:
        return self._set_active(code, is_active=False)

    def _set_active(self, code: str, *, is_active: bool) -> AppRegistryAppOut:
        row = self._get_required_app(code)
        row.is_active = is_active
        row.updated_at = datetime.now(UTC)
        self._commit_and_refresh(row)
        return _to_app_out(row)

    def _get_required_app(self, code: str) -> AppRegistryApp:
        row = self.repo.get_app(code)
        if row is None:
            raise AppRegistryAppNotFoundError("应用不存在")
        return row

    def _commit_and_refresh(self, row: AppRegistryApp) -> None:
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise AppRegistryAppSaveError("应用注册字段不符合数据库约束") from exc

        self.db.refresh(row)


__all__ = [
    "AppRegistryAdminService",
    "AppRegistryAppNotFoundError",
    "DuplicateAppRegistryAppError",
    "AppRegistryAppSaveError",
]
