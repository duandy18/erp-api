from __future__ import annotations

from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_self_description_projection import (
    AppRegistryAppManifestSnapshot,
    AppRegistryPageCatalogPage,
    AppRegistrySelfDescriptionSyncRun,
    AppRegistryServiceCapabilityCatalog,
    AppRegistryServiceCapabilityRoute,
    AppRegistryServiceDependencyCatalog,
    AppRegistryServiceDependencyEndpoint,
)


class AppRegistrySelfDescriptionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_app(self, code: str) -> AppRegistryApp | None:
        return (
            self.db.query(AppRegistryApp)
            .filter(AppRegistryApp.code == code)
            .one_or_none()
        )

    def get_manifest(self, app_code: str) -> AppRegistryAppManifestSnapshot | None:
        return (
            self.db.query(AppRegistryAppManifestSnapshot)
            .filter(AppRegistryAppManifestSnapshot.app_code == app_code)
            .one_or_none()
        )

    def list_pages(self, app_code: str) -> list[AppRegistryPageCatalogPage]:
        return (
            self.db.query(AppRegistryPageCatalogPage)
            .filter(AppRegistryPageCatalogPage.app_code == app_code)
            .order_by(
                AppRegistryPageCatalogPage.level.asc(),
                AppRegistryPageCatalogPage.sort_order.asc(),
                AppRegistryPageCatalogPage.page_code.asc(),
            )
            .all()
        )

    def list_capabilities(
        self,
        app_code: str,
    ) -> list[AppRegistryServiceCapabilityCatalog]:
        return (
            self.db.query(AppRegistryServiceCapabilityCatalog)
            .filter(AppRegistryServiceCapabilityCatalog.app_code == app_code)
            .order_by(AppRegistryServiceCapabilityCatalog.capability_code.asc())
            .all()
        )

    def list_capability_routes(
        self,
        app_code: str,
    ) -> list[AppRegistryServiceCapabilityRoute]:
        return (
            self.db.query(AppRegistryServiceCapabilityRoute)
            .filter(AppRegistryServiceCapabilityRoute.app_code == app_code)
            .order_by(
                AppRegistryServiceCapabilityRoute.capability_code.asc(),
                AppRegistryServiceCapabilityRoute.http_method.asc(),
                AppRegistryServiceCapabilityRoute.path.asc(),
            )
            .all()
        )

    def list_dependencies(
        self,
        source_app_code: str,
    ) -> list[AppRegistryServiceDependencyCatalog]:
        return (
            self.db.query(AppRegistryServiceDependencyCatalog)
            .filter(
                AppRegistryServiceDependencyCatalog.source_app_code
                == source_app_code
            )
            .order_by(AppRegistryServiceDependencyCatalog.dependency_code.asc())
            .all()
        )

    def list_dependency_endpoints(
        self,
        source_app_code: str,
    ) -> list[AppRegistryServiceDependencyEndpoint]:
        return (
            self.db.query(AppRegistryServiceDependencyEndpoint)
            .filter(
                AppRegistryServiceDependencyEndpoint.source_app_code
                == source_app_code
            )
            .order_by(
                AppRegistryServiceDependencyEndpoint.dependency_code.asc(),
                AppRegistryServiceDependencyEndpoint.http_method.asc(),
                AppRegistryServiceDependencyEndpoint.path.asc(),
            )
            .all()
        )

    def get_latest_sync_run(
        self,
        app_code: str,
    ) -> AppRegistrySelfDescriptionSyncRun | None:
        return (
            self.db.query(AppRegistrySelfDescriptionSyncRun)
            .filter(AppRegistrySelfDescriptionSyncRun.app_code == app_code)
            .order_by(
                AppRegistrySelfDescriptionSyncRun.started_at.desc(),
                AppRegistrySelfDescriptionSyncRun.id.desc(),
            )
            .first()
        )


__all__ = ["AppRegistrySelfDescriptionRepository"]
