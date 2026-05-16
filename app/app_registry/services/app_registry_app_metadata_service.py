from __future__ import annotations

from sqlalchemy.orm import Session

from app.app_registry.contracts.app_registry_app_metadata_contracts import (
    AppMetadataAppEnvironmentOut,
    AppMetadataAppOut,
    AppMetadataComponentOut,
    AppMetadataDatabaseOut,
    AppMetadataDependencyOut,
    AppMetadataEndpointOut,
    AppMetadataEnvironmentOut,
    AppMetadataGatewayBindingOut,
    AppMetadataHealthCheckOut,
    AppMetadataHealthCheckRunOut,
    AppMetadataOpenApiSourceOut,
    AppMetadataRepositoryOut,
    AppMetadataServiceClientOut,
    AppMetadataServicePermissionOut,
    AppRegistryAppMetadataListOut,
    AppRegistryAppMetadataOut,
)
from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryAppEnvironment,
    AppRegistryComponent,
    AppRegistryDatabase,
    AppRegistryDependency,
    AppRegistryEndpoint,
    AppRegistryEnvironment,
    AppRegistryGatewayBinding,
    AppRegistryHealthCheck,
    AppRegistryHealthCheckRun,
    AppRegistryOpenApiSource,
    AppRegistryRepositoryMeta,
    AppRegistryServiceClient,
    AppRegistryServicePermission,
)
from app.app_registry.repositories.app_registry_app_metadata_repository import (
    AppRegistryAppMetadataRepository,
)


class AppRegistryAppMetadataNotFoundError(ValueError):
    pass


def _app_out(row: AppRegistryApp) -> AppMetadataAppOut:
    return AppMetadataAppOut(
        code=str(row.code),
        name=str(row.name),
        description=str(row.description),
        web_path=str(row.web_path),
        api_path=str(row.api_path),
        local_web_url=str(row.local_web_url),
        local_api_url=str(row.local_api_url),
        status=str(row.status),
        domain_code=str(row.domain_code),
        app_type=str(row.app_type),
        owner_name=row.owner_name,
        owner_contact=row.owner_contact,
        sort_order=int(row.sort_order),
        is_active=bool(row.is_active),
    )


def _component_out(row: AppRegistryComponent) -> AppMetadataComponentOut:
    return AppMetadataComponentOut(
        id=int(row.id),
        app_code=str(row.app_code),
        component_code=str(row.component_code),
        component_type=str(row.component_type),
        name=str(row.name),
        description=str(row.description),
        is_required=bool(row.is_required),
        is_active=bool(row.is_active),
        sort_order=int(row.sort_order),
    )


def _environment_out(row: AppRegistryEnvironment) -> AppMetadataEnvironmentOut:
    return AppMetadataEnvironmentOut(
        env_code=str(row.env_code),
        name=str(row.name),
        description=str(row.description),
        sort_order=int(row.sort_order),
        is_active=bool(row.is_active),
    )


def _app_environment_out(row: AppRegistryAppEnvironment) -> AppMetadataAppEnvironmentOut:
    return AppMetadataAppEnvironmentOut(
        id=int(row.id),
        app_code=str(row.app_code),
        env_code=str(row.env_code),
        display_name=str(row.display_name),
        is_default=bool(row.is_default),
        is_active=bool(row.is_active),
        notes=row.notes,
    )


def _endpoint_out(row: AppRegistryEndpoint) -> AppMetadataEndpointOut:
    return AppMetadataEndpointOut(
        id=int(row.id),
        app_code=str(row.app_code),
        component_id=row.component_id,
        env_code=str(row.env_code),
        endpoint_type=str(row.endpoint_type),
        name=str(row.name),
        method=row.method,
        path=row.path,
        url=str(row.url),
        auth_required=bool(row.auth_required),
        timeout_ms=int(row.timeout_ms),
        is_active=bool(row.is_active),
        sort_order=int(row.sort_order),
    )


def _database_out(row: AppRegistryDatabase) -> AppMetadataDatabaseOut:
    return AppMetadataDatabaseOut(
        id=int(row.id),
        app_code=str(row.app_code),
        env_code=str(row.env_code),
        db_engine=str(row.db_engine),
        db_host_label=str(row.db_host_label),
        db_port=int(row.db_port),
        db_name=str(row.db_name),
        schema_name=str(row.schema_name),
        migration_tool=row.migration_tool,
        migration_command=row.migration_command,
        health_endpoint_id=row.health_endpoint_id,
        secret_ref=row.secret_ref,
        access_policy=str(row.access_policy),
        is_active=bool(row.is_active),
        notes=row.notes,
    )


def _repository_out(row: AppRegistryRepositoryMeta) -> AppMetadataRepositoryOut:
    return AppMetadataRepositoryOut(
        id=int(row.id),
        app_code=str(row.app_code),
        component_id=row.component_id,
        repo_type=str(row.repo_type),
        provider=str(row.provider),
        repo_owner=str(row.repo_owner),
        repo_name=str(row.repo_name),
        default_branch=str(row.default_branch),
        local_path=row.local_path,
        ci_workflow_name=row.ci_workflow_name,
        is_active=bool(row.is_active),
    )


def _gateway_binding_out(row: AppRegistryGatewayBinding) -> AppMetadataGatewayBindingOut:
    return AppMetadataGatewayBindingOut(
        id=int(row.id),
        app_code=str(row.app_code),
        env_code=str(row.env_code),
        web_path=str(row.web_path),
        api_path=str(row.api_path),
        web_upstream_url=row.web_upstream_url,
        api_upstream_url=row.api_upstream_url,
        rewrite_mode=str(row.rewrite_mode),
        is_published=bool(row.is_published),
        published_at=row.published_at,
        is_active=bool(row.is_active),
    )


def _dependency_out(row: AppRegistryDependency) -> AppMetadataDependencyOut:
    return AppMetadataDependencyOut(
        id=int(row.id),
        source_app_code=str(row.source_app_code),
        target_app_code=str(row.target_app_code),
        dependency_type=str(row.dependency_type),
        description=str(row.description),
        is_required=bool(row.is_required),
        status=str(row.status),
        is_active=bool(row.is_active),
    )


def _service_client_out(row: AppRegistryServiceClient) -> AppMetadataServiceClientOut:
    return AppMetadataServiceClientOut(
        id=int(row.id),
        app_code=str(row.app_code),
        client_code=str(row.client_code),
        client_name=str(row.client_name),
        auth_type=str(row.auth_type),
        secret_ref=row.secret_ref,
        is_active=bool(row.is_active),
    )


def _service_permission_out(
    row: AppRegistryServicePermission,
    client_by_id: dict[int, AppRegistryServiceClient],
) -> AppMetadataServicePermissionOut:
    client = client_by_id.get(int(row.client_id))

    return AppMetadataServicePermissionOut(
        id=int(row.id),
        client_id=int(row.client_id),
        client_code=str(client.client_code) if client is not None else None,
        client_name=str(client.client_name) if client is not None else None,
        source_app_code=str(row.source_app_code),
        target_app_code=str(row.target_app_code),
        permission_code=str(row.permission_code),
        description=str(row.description),
        is_active=bool(row.is_active),
    )


def _health_check_run_out(row: AppRegistryHealthCheckRun) -> AppMetadataHealthCheckRunOut:
    return AppMetadataHealthCheckRunOut(
        id=int(row.id),
        health_check_id=int(row.health_check_id),
        started_at=row.started_at,
        finished_at=row.finished_at,
        status=str(row.status),
        http_status=row.http_status,
        latency_ms=row.latency_ms,
        message=row.message,
        raw_excerpt=row.raw_excerpt,
    )


def _health_check_out(
    row: AppRegistryHealthCheck,
    latest_run_by_health_check_id: dict[int, AppRegistryHealthCheckRun],
) -> AppMetadataHealthCheckOut:
    latest_run = latest_run_by_health_check_id.get(int(row.id))

    return AppMetadataHealthCheckOut(
        id=int(row.id),
        app_code=str(row.app_code),
        env_code=str(row.env_code),
        endpoint_id=int(row.endpoint_id),
        check_type=str(row.check_type),
        expected_status=int(row.expected_status),
        expected_json_path=row.expected_json_path,
        expected_json_value=row.expected_json_value,
        timeout_ms=int(row.timeout_ms),
        interval_seconds=int(row.interval_seconds),
        severity=str(row.severity),
        is_active=bool(row.is_active),
        latest_run=_health_check_run_out(latest_run) if latest_run is not None else None,
    )


def _openapi_source_out(row: AppRegistryOpenApiSource) -> AppMetadataOpenApiSourceOut:
    return AppMetadataOpenApiSourceOut(
        id=int(row.id),
        app_code=str(row.app_code),
        env_code=str(row.env_code),
        endpoint_id=int(row.endpoint_id),
        openapi_url=str(row.openapi_url),
        last_fetched_at=row.last_fetched_at,
        last_checksum=row.last_checksum,
        last_status=str(row.last_status),
        is_active=bool(row.is_active),
    )


class AppRegistryAppMetadataService:
    def __init__(self, db: Session) -> None:
        self.repo = AppRegistryAppMetadataRepository(db)

    def list_profiles(self) -> AppRegistryAppMetadataListOut:
        return AppRegistryAppMetadataListOut(
            profiles=[self._build_profile(app) for app in self.repo.list_apps()]
        )

    def get_profile(self, app_code: str) -> AppRegistryAppMetadataOut:
        app = self.repo.get_app(app_code)
        if app is None:
            raise AppRegistryAppMetadataNotFoundError("应用主档不存在")
        return self._build_profile(app)

    def _build_profile(self, app: AppRegistryApp) -> AppRegistryAppMetadataOut:
        app_code = str(app.code)
        app_environments = self.repo.list_app_environments(app_code)
        env_codes = {row.env_code for row in app_environments}
        service_clients = self.repo.list_service_clients(app_code)
        service_permissions = self.repo.list_service_permissions(app_code)
        permission_client_ids = {int(row.client_id) for row in service_permissions}
        permission_clients = self.repo.list_service_clients_by_ids(permission_client_ids)
        client_by_id = {int(row.id): row for row in permission_clients}
        health_checks = self.repo.list_health_checks(app_code)
        health_check_ids = {int(row.id) for row in health_checks}
        latest_runs = self.repo.list_latest_health_check_runs(health_check_ids)
        latest_run_by_health_check_id: dict[int, AppRegistryHealthCheckRun] = {}

        for row in latest_runs:
            health_check_id = int(row.health_check_id)
            if health_check_id not in latest_run_by_health_check_id:
                latest_run_by_health_check_id[health_check_id] = row

        return AppRegistryAppMetadataOut(
            app=_app_out(app),
            components=[_component_out(row) for row in self.repo.list_components(app_code)],
            environments=[_environment_out(row) for row in self.repo.list_environments(env_codes)],
            app_environments=[_app_environment_out(row) for row in app_environments],
            endpoints=[_endpoint_out(row) for row in self.repo.list_endpoints(app_code)],
            databases=[_database_out(row) for row in self.repo.list_databases(app_code)],
            repositories=[_repository_out(row) for row in self.repo.list_repositories(app_code)],
            gateway_bindings=[
                _gateway_binding_out(row) for row in self.repo.list_gateway_bindings(app_code)
            ],
            outgoing_dependencies=[
                _dependency_out(row) for row in self.repo.list_outgoing_dependencies(app_code)
            ],
            incoming_dependencies=[
                _dependency_out(row) for row in self.repo.list_incoming_dependencies(app_code)
            ],
            service_clients=[_service_client_out(row) for row in service_clients],
            service_permissions=[
                _service_permission_out(row, client_by_id) for row in service_permissions
            ],
            health_checks=[
                _health_check_out(row, latest_run_by_health_check_id) for row in health_checks
            ],
            openapi_sources=[
                _openapi_source_out(row) for row in self.repo.list_openapi_sources(app_code)
            ],
        )


__all__ = [
    "AppRegistryAppMetadataNotFoundError",
    "AppRegistryAppMetadataService",
]
