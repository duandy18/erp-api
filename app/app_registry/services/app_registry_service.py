from __future__ import annotations

from sqlalchemy.orm import Session

from app.app_registry.contracts.app_registry_contracts import (
    AppRegistryAppOut,
    AppRegistryAppsOut,
)
from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.repositories.app_registry_repository import AppRegistryRepository


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


class AppRegistryService:
    def __init__(self, db: Session) -> None:
        self.repo = AppRegistryRepository(db)

    def list_apps(self) -> AppRegistryAppsOut:
        return AppRegistryAppsOut(
            apps=[_to_app_out(row) for row in self.repo.list_active_apps()]
        )


__all__ = ["AppRegistryService"]
