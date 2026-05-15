from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_system_metadata import (
    AppRegistryAppEnvironment,
    AppRegistryComponent,
    AppRegistryDatabase,
    AppRegistryDependency,
    AppRegistryEndpoint,
    AppRegistryEnvironment,
    AppRegistryGatewayBinding,
    AppRegistryRepositoryMeta,
    AppRegistryServiceClient,
    AppRegistryServicePermission,
)


class AppRegistrySystemProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_apps(self) -> list[AppRegistryApp]:
        return (
            self.db.query(AppRegistryApp)
            .order_by(AppRegistryApp.sort_order.asc(), AppRegistryApp.code.asc())
            .all()
        )

    def get_app(self, app_code: str) -> AppRegistryApp | None:
        return (
            self.db.query(AppRegistryApp)
            .filter(AppRegistryApp.code == app_code)
            .one_or_none()
        )

    def list_environments(self, env_codes: set[str]) -> list[AppRegistryEnvironment]:
        if not env_codes:
            return []

        return (
            self.db.query(AppRegistryEnvironment)
            .filter(AppRegistryEnvironment.env_code.in_(env_codes))
            .order_by(
                AppRegistryEnvironment.sort_order.asc(),
                AppRegistryEnvironment.env_code.asc(),
            )
            .all()
        )

    def list_app_environments(self, app_code: str) -> list[AppRegistryAppEnvironment]:
        return (
            self.db.query(AppRegistryAppEnvironment)
            .filter(AppRegistryAppEnvironment.app_code == app_code)
            .order_by(AppRegistryAppEnvironment.env_code.asc())
            .all()
        )

    def list_components(self, app_code: str) -> list[AppRegistryComponent]:
        return (
            self.db.query(AppRegistryComponent)
            .filter(AppRegistryComponent.app_code == app_code)
            .order_by(
                AppRegistryComponent.sort_order.asc(),
                AppRegistryComponent.component_code.asc(),
            )
            .all()
        )

    def list_endpoints(self, app_code: str) -> list[AppRegistryEndpoint]:
        return (
            self.db.query(AppRegistryEndpoint)
            .filter(AppRegistryEndpoint.app_code == app_code)
            .order_by(
                AppRegistryEndpoint.env_code.asc(),
                AppRegistryEndpoint.sort_order.asc(),
                AppRegistryEndpoint.endpoint_type.asc(),
                AppRegistryEndpoint.name.asc(),
            )
            .all()
        )

    def list_databases(self, app_code: str) -> list[AppRegistryDatabase]:
        return (
            self.db.query(AppRegistryDatabase)
            .filter(AppRegistryDatabase.app_code == app_code)
            .order_by(AppRegistryDatabase.env_code.asc(), AppRegistryDatabase.db_name.asc())
            .all()
        )

    def list_repositories(self, app_code: str) -> list[AppRegistryRepositoryMeta]:
        return (
            self.db.query(AppRegistryRepositoryMeta)
            .filter(AppRegistryRepositoryMeta.app_code == app_code)
            .order_by(
                AppRegistryRepositoryMeta.repo_type.asc(),
                AppRegistryRepositoryMeta.repo_name.asc(),
            )
            .all()
        )

    def list_gateway_bindings(self, app_code: str) -> list[AppRegistryGatewayBinding]:
        return (
            self.db.query(AppRegistryGatewayBinding)
            .filter(AppRegistryGatewayBinding.app_code == app_code)
            .order_by(
                AppRegistryGatewayBinding.env_code.asc(),
                AppRegistryGatewayBinding.web_path.asc(),
                AppRegistryGatewayBinding.api_path.asc(),
            )
            .all()
        )

    def list_outgoing_dependencies(self, app_code: str) -> list[AppRegistryDependency]:
        return (
            self.db.query(AppRegistryDependency)
            .filter(AppRegistryDependency.source_app_code == app_code)
            .order_by(
                AppRegistryDependency.target_app_code.asc(),
                AppRegistryDependency.dependency_type.asc(),
            )
            .all()
        )

    def list_incoming_dependencies(self, app_code: str) -> list[AppRegistryDependency]:
        return (
            self.db.query(AppRegistryDependency)
            .filter(AppRegistryDependency.target_app_code == app_code)
            .order_by(
                AppRegistryDependency.source_app_code.asc(),
                AppRegistryDependency.dependency_type.asc(),
            )
            .all()
        )

    def list_service_clients(self, app_code: str) -> list[AppRegistryServiceClient]:
        return (
            self.db.query(AppRegistryServiceClient)
            .filter(AppRegistryServiceClient.app_code == app_code)
            .order_by(AppRegistryServiceClient.client_code.asc())
            .all()
        )

    def list_service_clients_by_ids(self, client_ids: set[int]) -> list[AppRegistryServiceClient]:
        if not client_ids:
            return []

        return (
            self.db.query(AppRegistryServiceClient)
            .filter(AppRegistryServiceClient.id.in_(client_ids))
            .order_by(AppRegistryServiceClient.client_code.asc())
            .all()
        )

    def list_service_permissions(self, app_code: str) -> list[AppRegistryServicePermission]:
        return (
            self.db.query(AppRegistryServicePermission)
            .filter(
                or_(
                    AppRegistryServicePermission.source_app_code == app_code,
                    AppRegistryServicePermission.target_app_code == app_code,
                )
            )
            .order_by(
                AppRegistryServicePermission.source_app_code.asc(),
                AppRegistryServicePermission.target_app_code.asc(),
                AppRegistryServicePermission.permission_code.asc(),
            )
            .all()
        )


__all__ = ["AppRegistrySystemProfileRepository"]
