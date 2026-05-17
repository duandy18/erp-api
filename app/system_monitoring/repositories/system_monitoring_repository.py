from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryDatabase,
    AppRegistryDependency,
    AppRegistryEndpoint,
    AppRegistryGatewayBinding,
    AppRegistryHealthCheck,
    AppRegistryHealthCheckRun,
    AppRegistryOpenApiSource,
    AppRegistryServiceClient,
    AppRegistryServicePermission,
)


class SystemMonitoringRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_apps(self) -> list[AppRegistryApp]:
        return (
            self.db.query(AppRegistryApp)
            .order_by(AppRegistryApp.sort_order.asc(), AppRegistryApp.code.asc())
            .all()
        )

    def list_endpoints(self) -> list[AppRegistryEndpoint]:
        return (
            self.db.query(AppRegistryEndpoint)
            .order_by(
                AppRegistryEndpoint.app_code.asc(),
                AppRegistryEndpoint.env_code.asc(),
                AppRegistryEndpoint.endpoint_type.asc(),
                AppRegistryEndpoint.name.asc(),
            )
            .all()
        )

    def list_databases(self) -> list[AppRegistryDatabase]:
        return (
            self.db.query(AppRegistryDatabase)
            .order_by(
                AppRegistryDatabase.app_code.asc(),
                AppRegistryDatabase.env_code.asc(),
                AppRegistryDatabase.db_name.asc(),
            )
            .all()
        )

    def list_gateway_bindings(self) -> list[AppRegistryGatewayBinding]:
        return (
            self.db.query(AppRegistryGatewayBinding)
            .order_by(
                AppRegistryGatewayBinding.app_code.asc(),
                AppRegistryGatewayBinding.env_code.asc(),
                AppRegistryGatewayBinding.web_path.asc(),
                AppRegistryGatewayBinding.api_path.asc(),
            )
            .all()
        )

    def list_dependencies(self) -> list[AppRegistryDependency]:
        return (
            self.db.query(AppRegistryDependency)
            .order_by(
                AppRegistryDependency.source_app_code.asc(),
                AppRegistryDependency.target_app_code.asc(),
                AppRegistryDependency.dependency_type.asc(),
            )
            .all()
        )

    def list_service_clients(self) -> list[AppRegistryServiceClient]:
        return (
            self.db.query(AppRegistryServiceClient)
            .order_by(
                AppRegistryServiceClient.app_code.asc(),
                AppRegistryServiceClient.client_code.asc(),
            )
            .all()
        )

    def list_service_permissions(self) -> list[AppRegistryServicePermission]:
        return (
            self.db.query(AppRegistryServicePermission)
            .filter(
                or_(
                    AppRegistryServicePermission.source_app_code.is_not(None),
                    AppRegistryServicePermission.target_app_code.is_not(None),
                )
            )
            .order_by(
                AppRegistryServicePermission.source_app_code.asc(),
                AppRegistryServicePermission.target_app_code.asc(),
                AppRegistryServicePermission.permission_code.asc(),
            )
            .all()
        )

    def list_health_checks(self) -> list[AppRegistryHealthCheck]:
        return (
            self.db.query(AppRegistryHealthCheck)
            .order_by(
                AppRegistryHealthCheck.app_code.asc(),
                AppRegistryHealthCheck.env_code.asc(),
                AppRegistryHealthCheck.endpoint_id.asc(),
                AppRegistryHealthCheck.check_type.asc(),
            )
            .all()
        )

    def list_latest_health_check_runs(
        self,
        health_check_ids: set[int],
    ) -> list[AppRegistryHealthCheckRun]:
        if not health_check_ids:
            return []

        return (
            self.db.query(AppRegistryHealthCheckRun)
            .filter(AppRegistryHealthCheckRun.health_check_id.in_(health_check_ids))
            .order_by(
                AppRegistryHealthCheckRun.health_check_id.asc(),
                AppRegistryHealthCheckRun.started_at.desc(),
                AppRegistryHealthCheckRun.id.desc(),
            )
            .all()
        )

    def list_openapi_sources(self) -> list[AppRegistryOpenApiSource]:
        return (
            self.db.query(AppRegistryOpenApiSource)
            .order_by(
                AppRegistryOpenApiSource.app_code.asc(),
                AppRegistryOpenApiSource.env_code.asc(),
                AppRegistryOpenApiSource.endpoint_id.asc(),
            )
            .all()
        )


__all__ = ["SystemMonitoringRepository"]
