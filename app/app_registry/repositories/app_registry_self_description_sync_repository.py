from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_self_description_projection import (
    AppRegistryAppManifestSnapshot,
    AppRegistryPageCatalogPage,
    AppRegistryServiceCapabilityCatalog,
    AppRegistryServiceCapabilityRoute,
    AppRegistryServiceDependencyCatalog,
    AppRegistryServiceDependencyEndpoint,
)


class AppRegistrySelfDescriptionSyncSaveError(ValueError):
    pass


class AppRegistrySelfDescriptionSyncRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_app(self, code: str) -> AppRegistryApp | None:
        return (
            self.db.query(AppRegistryApp)
            .filter(AppRegistryApp.code == code)
            .one_or_none()
        )

    def get_manifest_snapshot(
        self,
        app_code: str,
    ) -> AppRegistryAppManifestSnapshot | None:
        return (
            self.db.query(AppRegistryAppManifestSnapshot)
            .filter(AppRegistryAppManifestSnapshot.app_code == app_code)
            .one_or_none()
        )

    def list_page_catalog_pages(self, app_code: str) -> list[AppRegistryPageCatalogPage]:
        return (
            self.db.query(AppRegistryPageCatalogPage)
            .filter(AppRegistryPageCatalogPage.app_code == app_code)
            .all()
        )

    def list_service_capabilities(
        self,
        app_code: str,
    ) -> list[AppRegistryServiceCapabilityCatalog]:
        return (
            self.db.query(AppRegistryServiceCapabilityCatalog)
            .filter(AppRegistryServiceCapabilityCatalog.app_code == app_code)
            .all()
        )

    def list_service_capability_routes(
        self,
        app_code: str,
    ) -> list[AppRegistryServiceCapabilityRoute]:
        return (
            self.db.query(AppRegistryServiceCapabilityRoute)
            .filter(AppRegistryServiceCapabilityRoute.app_code == app_code)
            .all()
        )

    def list_service_dependencies(
        self,
        source_app_code: str,
    ) -> list[AppRegistryServiceDependencyCatalog]:
        return (
            self.db.query(AppRegistryServiceDependencyCatalog)
            .filter(AppRegistryServiceDependencyCatalog.source_app_code == source_app_code)
            .all()
        )

    def list_service_dependency_endpoints(
        self,
        source_app_code: str,
    ) -> list[AppRegistryServiceDependencyEndpoint]:
        return (
            self.db.query(AppRegistryServiceDependencyEndpoint)
            .filter(AppRegistryServiceDependencyEndpoint.source_app_code == source_app_code)
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
            raise AppRegistrySelfDescriptionSyncSaveError("自描述同步数据写入失败") from exc

    def commit(self) -> None:
        try:
            self.db.commit()
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise AppRegistrySelfDescriptionSyncSaveError("自描述同步数据保存失败") from exc

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, row: object) -> None:
        self.db.refresh(row)


__all__ = [
    "AppRegistrySelfDescriptionSyncRepository",
    "AppRegistrySelfDescriptionSyncSaveError",
]
