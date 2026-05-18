from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_self_description_projection import (
    AppRegistryServiceCapabilityCatalog,
    AppRegistryServiceCapabilityRoute,
)
from app.system_service_auth.contracts.system_service_auth_capability_contracts import (
    SystemServiceAuthCapabilityListOut,
    SystemServiceAuthCapabilityOut,
    SystemServiceAuthCapabilityRouteOut,
)
from app.system_service_auth.repositories.system_service_auth_capability_repository import (
    SystemServiceAuthCapabilityRepository,
)


def _normalize_app_code(value: str | None) -> str | None:
    if value is None:
        return None

    stripped = value.strip()
    return stripped or None


class SystemServiceAuthCapabilityService:
    def __init__(
        self,
        db: Session,
        *,
        repository: SystemServiceAuthCapabilityRepository | None = None,
    ) -> None:
        self.repo = repository or SystemServiceAuthCapabilityRepository(db)

    def list_capabilities(
        self,
        *,
        target_app_code: str | None = None,
    ) -> SystemServiceAuthCapabilityListOut:
        normalized_target = _normalize_app_code(target_app_code)
        capabilities = self.repo.list_capabilities(target_app_code=normalized_target)
        routes = self.repo.list_routes(target_app_code=normalized_target)

        app_codes = {str(row.app_code) for row in capabilities}
        app_by_code = {str(row.code): row for row in self.repo.list_apps_by_codes(app_codes)}
        routes_by_identity = self._group_routes(routes)

        return SystemServiceAuthCapabilityListOut(
            capabilities=[
                self._capability_out(
                    row=row,
                    app_by_code=app_by_code,
                    routes=routes_by_identity.get(
                        (str(row.app_code), str(row.capability_code)),
                        [],
                    ),
                )
                for row in capabilities
            ]
        )

    @staticmethod
    def _group_routes(
        rows: Sequence[AppRegistryServiceCapabilityRoute],
    ) -> dict[tuple[str, str], list[AppRegistryServiceCapabilityRoute]]:
        grouped: dict[tuple[str, str], list[AppRegistryServiceCapabilityRoute]] = defaultdict(list)

        for row in rows:
            grouped[(str(row.app_code), str(row.capability_code))].append(row)

        return dict(grouped)

    @classmethod
    def _capability_out(
        cls,
        *,
        row: AppRegistryServiceCapabilityCatalog,
        app_by_code: dict[str, AppRegistryApp],
        routes: Sequence[AppRegistryServiceCapabilityRoute],
    ) -> SystemServiceAuthCapabilityOut:
        target_app_code = str(row.app_code)
        target_app = app_by_code.get(target_app_code)

        route_out = [cls._route_out(route) for route in routes]

        return SystemServiceAuthCapabilityOut(
            target_app_code=target_app_code,
            target_app_name=str(target_app.name) if target_app is not None else target_app_code,
            capability_code=str(row.capability_code),
            capability_name=str(row.capability_name),
            resource_code=str(row.resource_code),
            permission_code=str(row.permission_code),
            description=row.description,
            is_active=bool(row.is_active),
            source_updated_at=row.source_updated_at,
            last_synced_at=row.last_synced_at,
            route_count=len(route_out),
            routes=route_out,
        )

    @staticmethod
    def _route_out(
        row: AppRegistryServiceCapabilityRoute,
    ) -> SystemServiceAuthCapabilityRouteOut:
        return SystemServiceAuthCapabilityRouteOut(
            http_method=str(row.http_method),
            path=str(row.path),
            route_name=str(row.route_name),
            auth_required=bool(row.auth_required),
            is_active=bool(row.is_active),
            source_created_at=row.source_created_at,
            last_synced_at=row.last_synced_at,
        )


__all__ = ["SystemServiceAuthCapabilityService"]
