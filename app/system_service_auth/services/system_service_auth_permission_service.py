from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryServiceClient,
    AppRegistryServicePermission,
)
from app.app_registry.models.app_registry_self_description_projection import (
    AppRegistryServiceCapabilityCatalog,
)
from app.system_service_auth.contracts.system_service_auth_permission_contracts import (
    SystemServiceAuthCapabilityOptionOut,
    SystemServiceAuthClientOut,
    SystemServiceAuthPermissionCreateIn,
    SystemServiceAuthPermissionListOut,
    SystemServiceAuthPermissionOut,
    SystemServiceAuthPermissionUpdateIn,
)
from app.system_service_auth.repositories.system_service_auth_permission_repository import (
    DuplicateSystemServiceAuthPermissionError,
    SystemServiceAuthPermissionRepository,
    SystemServiceAuthPermissionSaveError,
)


class SystemServiceAuthClientNotFoundError(ValueError):
    pass


class SystemServiceAuthPermissionNotFoundError(ValueError):
    pass


class SystemServiceAuthCapabilityNotFoundError(ValueError):
    pass


class SystemServiceAuthPermissionValidationError(ValueError):
    pass


def _trim(value: str, field_name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise SystemServiceAuthPermissionValidationError(f"{field_name}不能为空")
    return stripped


def _app_name(app_by_code: dict[str, AppRegistryApp], app_code: object) -> str:
    code = str(app_code)
    row = app_by_code.get(code)
    return str(row.name) if row is not None else code


class SystemServiceAuthPermissionService:
    def __init__(
        self,
        db: Session,
        *,
        repository: SystemServiceAuthPermissionRepository | None = None,
    ) -> None:
        self.repo = repository or SystemServiceAuthPermissionRepository(db)

    def list_permissions(self) -> SystemServiceAuthPermissionListOut:
        apps = self.repo.list_apps()
        clients = self.repo.list_clients()
        capability_options = self.repo.list_capability_options()
        permissions = self.repo.list_permissions()

        app_by_code = {str(row.code): row for row in apps}
        client_by_id = {int(row.id): row for row in clients}
        capability_by_identity = {
            (str(row.app_code), str(row.permission_code)): row
            for row in capability_options
        }

        return SystemServiceAuthPermissionListOut(
            clients=[
                self._client_out(row=row, app_by_code=app_by_code)
                for row in clients
            ],
            capability_options=[
                self._capability_option_out(row=row, app_by_code=app_by_code)
                for row in capability_options
            ],
            permissions=[
                self._permission_out(
                    row=row,
                    app_by_code=app_by_code,
                    client_by_id=client_by_id,
                    capability_by_identity=capability_by_identity,
                )
                for row in permissions
            ],
        )

    def create_permission(
        self,
        body: SystemServiceAuthPermissionCreateIn,
    ) -> SystemServiceAuthPermissionOut:
        client = self.repo.get_client(body.client_id)
        if client is None:
            raise SystemServiceAuthClientNotFoundError("service client 不存在")

        target_app_code = _trim(body.target_app_code, "target_app_code")
        permission_code = _trim(body.permission_code, "permission_code")
        description = _trim(body.description, "description")

        capability = self.repo.get_capability_by_permission(
            target_app_code=target_app_code,
            permission_code=permission_code,
        )
        if capability is None:
            raise SystemServiceAuthCapabilityNotFoundError("目标系统能力不存在")

        existing = self.repo.find_permission(
            client_id=int(client.id),
            permission_code=permission_code,
        )
        if existing is not None:
            raise DuplicateSystemServiceAuthPermissionError("该 client 已存在相同授权")

        row = AppRegistryServicePermission(
            client_id=int(client.id),
            source_app_code=str(client.app_code),
            target_app_code=target_app_code,
            permission_code=permission_code,
            description=description,
            is_active=bool(body.is_active),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        saved = self.repo.save_permission(row)
        return self._permission_out_with_context(saved)

    def update_permission(
        self,
        permission_id: int,
        body: SystemServiceAuthPermissionUpdateIn,
    ) -> SystemServiceAuthPermissionOut:
        row = self.repo.get_permission(permission_id)
        if row is None:
            raise SystemServiceAuthPermissionNotFoundError("系统调用授权不存在")

        if "description" in body.model_fields_set and body.description is not None:
            row.description = _trim(body.description, "description")

        if "is_active" in body.model_fields_set and body.is_active is not None:
            row.is_active = bool(body.is_active)

        row.updated_at = datetime.now(UTC)

        saved = self.repo.save_permission(row)
        return self._permission_out_with_context(saved)

    def _permission_out_with_context(
        self,
        row: AppRegistryServicePermission,
    ) -> SystemServiceAuthPermissionOut:
        apps = self.repo.list_apps()
        clients = self.repo.list_clients()
        capabilities = self.repo.list_capability_options()

        return self._permission_out(
            row=row,
            app_by_code={str(app.code): app for app in apps},
            client_by_id={int(client.id): client for client in clients},
            capability_by_identity={
                (str(capability.app_code), str(capability.permission_code)): capability
                for capability in capabilities
            },
        )

    @staticmethod
    def _client_out(
        *,
        row: AppRegistryServiceClient,
        app_by_code: dict[str, AppRegistryApp],
    ) -> SystemServiceAuthClientOut:
        return SystemServiceAuthClientOut(
            client_id=int(row.id),
            app_code=str(row.app_code),
            app_name=_app_name(app_by_code, row.app_code),
            client_code=str(row.client_code),
            client_name=str(row.client_name),
            auth_type=str(row.auth_type),
            secret_ref=row.secret_ref,
            is_active=bool(row.is_active),
        )

    @staticmethod
    def _capability_option_out(
        *,
        row: AppRegistryServiceCapabilityCatalog,
        app_by_code: dict[str, AppRegistryApp],
    ) -> SystemServiceAuthCapabilityOptionOut:
        return SystemServiceAuthCapabilityOptionOut(
            target_app_code=str(row.app_code),
            target_app_name=_app_name(app_by_code, row.app_code),
            capability_code=str(row.capability_code),
            capability_name=str(row.capability_name),
            permission_code=str(row.permission_code),
            description=row.description,
            is_active=bool(row.is_active),
            last_synced_at=row.last_synced_at,
        )

    @staticmethod
    def _permission_out(
        *,
        row: AppRegistryServicePermission,
        app_by_code: dict[str, AppRegistryApp],
        client_by_id: dict[int, AppRegistryServiceClient],
        capability_by_identity: dict[tuple[str, str], AppRegistryServiceCapabilityCatalog],
    ) -> SystemServiceAuthPermissionOut:
        client = client_by_id.get(int(row.client_id))
        capability = capability_by_identity.get(
            (str(row.target_app_code), str(row.permission_code))
        )

        return SystemServiceAuthPermissionOut(
            permission_id=int(row.id),
            client_id=int(row.client_id),
            client_code=str(client.client_code) if client is not None else None,
            source_app_code=str(row.source_app_code),
            source_app_name=_app_name(app_by_code, row.source_app_code),
            target_app_code=str(row.target_app_code),
            target_app_name=_app_name(app_by_code, row.target_app_code),
            permission_code=str(row.permission_code),
            description=str(row.description),
            is_active=bool(row.is_active),
            created_at=row.created_at,
            updated_at=row.updated_at,
            capability_code=str(capability.capability_code) if capability is not None else None,
            capability_name=str(capability.capability_name) if capability is not None else None,
            capability_active=bool(capability.is_active) if capability is not None else None,
        )


__all__ = [
    "DuplicateSystemServiceAuthPermissionError",
    "SystemServiceAuthCapabilityNotFoundError",
    "SystemServiceAuthClientNotFoundError",
    "SystemServiceAuthPermissionNotFoundError",
    "SystemServiceAuthPermissionSaveError",
    "SystemServiceAuthPermissionService",
    "SystemServiceAuthPermissionValidationError",
]
