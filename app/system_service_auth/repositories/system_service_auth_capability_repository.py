from __future__ import annotations

from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_self_description_projection import (
    AppRegistryServiceCapabilityCatalog,
    AppRegistryServiceCapabilityRoute,
)


class SystemServiceAuthCapabilityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_apps_by_codes(self, app_codes: set[str]) -> list[AppRegistryApp]:
        if not app_codes:
            return []

        return (
            self.db.query(AppRegistryApp)
            .filter(AppRegistryApp.code.in_(sorted(app_codes)))
            .order_by(AppRegistryApp.sort_order.asc(), AppRegistryApp.code.asc())
            .all()
        )

    def list_capabilities(
        self,
        *,
        target_app_code: str | None = None,
    ) -> list[AppRegistryServiceCapabilityCatalog]:
        query = self.db.query(AppRegistryServiceCapabilityCatalog)

        if target_app_code:
            query = query.filter(AppRegistryServiceCapabilityCatalog.app_code == target_app_code)

        return (
            query.order_by(
                AppRegistryServiceCapabilityCatalog.app_code.asc(),
                AppRegistryServiceCapabilityCatalog.capability_code.asc(),
            )
            .all()
        )

    def list_routes(
        self,
        *,
        target_app_code: str | None = None,
    ) -> list[AppRegistryServiceCapabilityRoute]:
        query = self.db.query(AppRegistryServiceCapabilityRoute)

        if target_app_code:
            query = query.filter(AppRegistryServiceCapabilityRoute.app_code == target_app_code)

        return (
            query.order_by(
                AppRegistryServiceCapabilityRoute.app_code.asc(),
                AppRegistryServiceCapabilityRoute.capability_code.asc(),
                AppRegistryServiceCapabilityRoute.http_method.asc(),
                AppRegistryServiceCapabilityRoute.path.asc(),
            )
            .all()
        )


__all__ = ["SystemServiceAuthCapabilityRepository"]
