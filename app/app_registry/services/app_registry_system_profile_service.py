from __future__ import annotations

from sqlalchemy.orm import Session

from app.app_registry.contracts.app_registry_system_profile_contracts import (
    AppRegistrySystemProfileOut,
    AppRegistrySystemProfilesOut,
    SystemProfileAppEnvironmentOut,
    SystemProfileAppOut,
    SystemProfileComponentOut,
    SystemProfileDatabaseOut,
    SystemProfileDependencyOut,
    SystemProfileEndpointOut,
    SystemProfileEnvironmentOut,
    SystemProfileGatewayBindingOut,
    SystemProfileRepositoryOut,
    SystemProfileServiceClientOut,
    SystemProfileServicePermissionOut,
)
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
from app.app_registry.repositories.app_registry_system_profile_repository import (
    AppRegistrySystemProfileRepository,
)


class AppRegistrySystemProfileNotFoundError(ValueError):
    pass


def _app_out(row: AppRegistryApp) -> SystemProfileAppOut:
    return SystemProfileAppOut(
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


def _component_out(row: AppRegistryComponent) -> SystemProfileComponentOut:
    return SystemProfileComponentOut(
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


def _environment_out(row: AppRegistryEnvironment) -> SystemProfileEnvironmentOut:
    return SystemProfileEnvironmentOut(
        env_code=str(row.env_code),
        name=str(row.name),
        description=str(row.description),
        sort_order=int(row.sort_order),
        is_active=bool(row.is_active),
    )


def _app_environment_out(row: AppRegistryAppEnvironment) -> SystemProfileAppEnvironmentOut:
    return SystemProfileAppEnvironmentOut(
        id=int(row.id),
        app_code=str(row.app_code),
        env_code=str(row.env_code),
        display_name=str(row.display_name),
        is_default=bool(row.is_default),
        is_active=bool(row.is_active),
        notes=row.notes,
    )


def _endpoint_out(row: AppRegistryEndpoint) -> SystemProfileEndpointOut:
    return SystemProfileEndpointOut(
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


def _database_out(row: AppRegistryDatabase) -> SystemProfileDatabaseOut:
    return SystemProfileDatabaseOut(
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


def _repository_out(row: AppRegistryRepositoryMeta) -> SystemProfileRepositoryOut:
    return SystemProfileRepositoryOut(
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


def _gateway_binding_out(row: AppRegistryGatewayBinding) -> SystemProfileGatewayBindingOut:
    return SystemProfileGatewayBindingOut(
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


def _dependency_out(row: AppRegistryDependency) -> SystemProfileDependencyOut:
    return SystemProfileDependencyOut(
        id=int(row.id),
        source_app_code=str(row.source_app_code),
        target_app_code=str(row.target_app_code),
        dependency_type=str(row.dependency_type),
        description=str(row.description),
        is_required=bool(row.is_required),
        status=str(row.status),
        is_active=bool(row.is_active),
    )


def _service_client_out(row: AppRegistryServiceClient) -> SystemProfileServiceClientOut:
    return SystemProfileServiceClientOut(
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
) -> SystemProfileServicePermissionOut:
    client = client_by_id.get(int(row.client_id))

    return SystemProfileServicePermissionOut(
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


class AppRegistrySystemProfileService:
    def __init__(self, db: Session) -> None:
        self.repo = AppRegistrySystemProfileRepository(db)

    def list_profiles(self) -> AppRegistrySystemProfilesOut:
        return AppRegistrySystemProfilesOut(
            profiles=[self._build_profile(app) for app in self.repo.list_apps()]
        )

    def get_profile(self, app_code: str) -> AppRegistrySystemProfileOut:
        app = self.repo.get_app(app_code)
        if app is None:
            raise AppRegistrySystemProfileNotFoundError("系统档案不存在")
        return self._build_profile(app)

    def _build_profile(self, app: AppRegistryApp) -> AppRegistrySystemProfileOut:
        app_code = str(app.code)
        app_environments = self.repo.list_app_environments(app_code)
        env_codes = {row.env_code for row in app_environments}
        service_clients = self.repo.list_service_clients(app_code)
        service_permissions = self.repo.list_service_permissions(app_code)
        permission_client_ids = {int(row.client_id) for row in service_permissions}
        permission_clients = self.repo.list_service_clients_by_ids(permission_client_ids)
        client_by_id = {int(row.id): row for row in permission_clients}

        return AppRegistrySystemProfileOut(
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
        )


__all__ = [
    "AppRegistrySystemProfileNotFoundError",
    "AppRegistrySystemProfileService",
]
