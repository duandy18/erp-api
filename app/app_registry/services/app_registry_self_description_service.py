from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from typing import Any

from sqlalchemy.orm import Session

from app.app_registry.contracts.app_registry_self_description_contracts import (
    AppRegistrySelfDescriptionCapabilityOut,
    AppRegistrySelfDescriptionCapabilityRouteOut,
    AppRegistrySelfDescriptionDependencyEndpointOut,
    AppRegistrySelfDescriptionDependencyOut,
    AppRegistrySelfDescriptionManifestOut,
    AppRegistrySelfDescriptionOut,
    AppRegistrySelfDescriptionPageOut,
)
from app.app_registry.models.app_registry_self_description_projection import (
    AppRegistryAppManifestSnapshot,
    AppRegistryPageCatalogPage,
    AppRegistrySelfDescriptionSyncRun,
    AppRegistryServiceCapabilityCatalog,
    AppRegistryServiceCapabilityRoute,
    AppRegistryServiceDependencyCatalog,
    AppRegistryServiceDependencyEndpoint,
)
from app.app_registry.repositories.app_registry_self_description_repository import (
    AppRegistrySelfDescriptionRepository,
)
from app.app_registry.services.app_registry_self_description_sync_service import (
    _run_out,
)


class AppRegistrySelfDescriptionNotFoundError(ValueError):
    pass


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    result: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            result.append(item.strip())
    return result


class AppRegistrySelfDescriptionService:
    def __init__(
        self,
        db: Session,
        *,
        repository: AppRegistrySelfDescriptionRepository | None = None,
    ) -> None:
        self.repo = repository or AppRegistrySelfDescriptionRepository(db)

    def get_app_self_description(self, code: str) -> AppRegistrySelfDescriptionOut:
        app_code = code.strip()
        app_row = self.repo.get_app(app_code)
        if app_row is None:
            raise AppRegistrySelfDescriptionNotFoundError("应用不存在")

        routes_by_capability = self._group_capability_routes(
            self.repo.list_capability_routes(app_code)
        )
        endpoints_by_dependency = self._group_dependency_endpoints(
            self.repo.list_dependency_endpoints(app_code)
        )

        latest_sync_run = self.repo.get_latest_sync_run(app_code)

        return AppRegistrySelfDescriptionOut(
            app_code=str(app_row.code),
            app_name=str(app_row.name),
            manifest=self._manifest_out(self.repo.get_manifest(app_code)),
            pages=[self._page_out(row) for row in self.repo.list_pages(app_code)],
            capabilities=[
                self._capability_out(
                    row,
                    routes_by_capability.get(str(row.capability_code), []),
                )
                for row in self.repo.list_capabilities(app_code)
            ],
            dependencies=[
                self._dependency_out(
                    row,
                    endpoints_by_dependency.get(str(row.dependency_code), []),
                )
                for row in self.repo.list_dependencies(app_code)
            ],
            latest_sync_run=self._sync_run_out(latest_sync_run),
        )

    @staticmethod
    def _manifest_out(
        row: AppRegistryAppManifestSnapshot | None,
    ) -> AppRegistrySelfDescriptionManifestOut | None:
        if row is None:
            return None

        return AppRegistrySelfDescriptionManifestOut(
            app_code=str(row.app_code),
            app_name=str(row.app_name),
            app_type=str(row.app_type),
            status=str(row.status),
            description=str(row.description),
            default_web_path=str(row.default_web_path),
            default_api_path=str(row.default_api_path),
            local_web_url=str(row.local_web_url),
            local_api_url=str(row.local_api_url),
            health_url=str(row.health_url),
            db_health_url=row.db_health_url,
            openapi_url=str(row.openapi_url),
            page_catalog_url=str(row.page_catalog_url),
            service_capabilities_url=str(row.service_capabilities_url),
            service_dependencies_url=str(row.service_dependencies_url),
            version=str(row.version),
            build_environment=row.build_environment,
            build_git_sha=row.build_git_sha,
            build_time=row.build_time,
            last_synced_at=row.last_synced_at,
        )

    @staticmethod
    def _page_out(row: AppRegistryPageCatalogPage) -> AppRegistrySelfDescriptionPageOut:
        return AppRegistrySelfDescriptionPageOut(
            page_code=str(row.page_code),
            page_name=str(row.page_name),
            route_path=row.route_path,
            parent_page_code=row.parent_page_code,
            level=int(row.level),
            read_permission_code=row.read_permission_code,
            write_permission_code=row.write_permission_code,
            is_active=bool(row.is_active),
            sort_order=int(row.sort_order),
            source_updated_at=row.source_updated_at,
            last_synced_at=row.last_synced_at,
        )

    @staticmethod
    def _group_capability_routes(
        rows: Sequence[AppRegistryServiceCapabilityRoute],
    ) -> dict[str, list[AppRegistryServiceCapabilityRoute]]:
        grouped: dict[str, list[AppRegistryServiceCapabilityRoute]] = defaultdict(list)
        for row in rows:
            grouped[str(row.capability_code)].append(row)
        return dict(grouped)

    @classmethod
    def _capability_out(
        cls,
        row: AppRegistryServiceCapabilityCatalog,
        routes: Sequence[AppRegistryServiceCapabilityRoute],
    ) -> AppRegistrySelfDescriptionCapabilityOut:
        return AppRegistrySelfDescriptionCapabilityOut(
            capability_code=str(row.capability_code),
            capability_name=str(row.capability_name),
            resource_code=str(row.resource_code),
            permission_code=str(row.permission_code),
            description=row.description,
            is_active=bool(row.is_active),
            source_updated_at=row.source_updated_at,
            last_synced_at=row.last_synced_at,
            routes=[cls._capability_route_out(route) for route in routes],
        )

    @staticmethod
    def _capability_route_out(
        row: AppRegistryServiceCapabilityRoute,
    ) -> AppRegistrySelfDescriptionCapabilityRouteOut:
        return AppRegistrySelfDescriptionCapabilityRouteOut(
            http_method=str(row.http_method),
            path=str(row.path),
            route_name=str(row.route_name),
            auth_required=bool(row.auth_required),
            is_active=bool(row.is_active),
            source_created_at=row.source_created_at,
            last_synced_at=row.last_synced_at,
        )

    @staticmethod
    def _group_dependency_endpoints(
        rows: Sequence[AppRegistryServiceDependencyEndpoint],
    ) -> dict[str, list[AppRegistryServiceDependencyEndpoint]]:
        grouped: dict[str, list[AppRegistryServiceDependencyEndpoint]] = defaultdict(list)
        for row in rows:
            grouped[str(row.dependency_code)].append(row)
        return dict(grouped)

    @classmethod
    def _dependency_out(
        cls,
        row: AppRegistryServiceDependencyCatalog,
        endpoints: Sequence[AppRegistryServiceDependencyEndpoint],
    ) -> AppRegistrySelfDescriptionDependencyOut:
        return AppRegistrySelfDescriptionDependencyOut(
            dependency_code=str(row.dependency_code),
            dependency_name=str(row.dependency_name),
            target_app_code=str(row.target_app_code),
            target_capability_code=str(row.target_capability_code),
            required_permission_code=str(row.required_permission_code),
            description=row.description,
            is_required=bool(row.is_required),
            is_active=bool(row.is_active),
            required_config_keys=_string_list(row.required_config_keys),
            source_modules=_string_list(row.source_modules),
            last_synced_at=row.last_synced_at,
            endpoints=[cls._dependency_endpoint_out(endpoint) for endpoint in endpoints],
        )

    @staticmethod
    def _dependency_endpoint_out(
        row: AppRegistryServiceDependencyEndpoint,
    ) -> AppRegistrySelfDescriptionDependencyEndpointOut:
        return AppRegistrySelfDescriptionDependencyEndpointOut(
            http_method=str(row.http_method),
            path=str(row.path),
            purpose=row.purpose,
            last_synced_at=row.last_synced_at,
        )

    @staticmethod
    def _sync_run_out(row: AppRegistrySelfDescriptionSyncRun | None):
        if row is None:
            return None
        return _run_out(row)


__all__ = [
    "AppRegistrySelfDescriptionNotFoundError",
    "AppRegistrySelfDescriptionService",
]
