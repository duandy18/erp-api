from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from app.app_registry.models.app_registry_iam_projection import (
    AppRegistryIamPageProjection,
    AppRegistryIamPageRoutePrefixProjection,
    AppRegistryIamPermissionProjection,
    AppRegistryIamSyncRun,
    AppRegistryIamUserPermissionProjection,
    AppRegistryIamUserProjection,
)
from app.system_iam.contracts import SystemIamSyncRunOut
from app.system_iam.services import SystemIamSnapshotSyncService
from app.system_iam.services.iam_snapshot_sync_service import (
    ERP_SERVICE_CLIENT,
    IAM_SNAPSHOT_PATH,
)


class FakeSyncRepo:
    def __init__(self) -> None:
        self.app = SimpleNamespace(code="wms", local_api_url="http://127.0.0.1:8000/")
        self.run: AppRegistryIamSyncRun | None = None
        self.users: list[AppRegistryIamUserProjection] = []
        self.permissions: list[AppRegistryIamPermissionProjection] = []
        self.user_permissions: list[AppRegistryIamUserPermissionProjection] = []
        self.pages: list[AppRegistryIamPageProjection] = []
        self.route_prefixes: list[AppRegistryIamPageRoutePrefixProjection] = []
        self.committed = False
        self.refreshed = False

    def get_app(self, code: str):
        return self.app if code == "wms" else None

    def list_users(self, app_code: str):
        return list(self.users) if app_code == "wms" else []

    def list_permissions(self, app_code: str):
        return list(self.permissions) if app_code == "wms" else []

    def list_user_permissions(self, app_code: str):
        return list(self.user_permissions) if app_code == "wms" else []

    def list_pages(self, app_code: str):
        return list(self.pages) if app_code == "wms" else []

    def list_route_prefixes(self, app_code: str):
        return list(self.route_prefixes) if app_code == "wms" else []

    def add(self, row: object) -> None:
        table_name = row.__table__.name
        if table_name == "app_registry_iam_sync_runs":
            self.run = row
            return
        if table_name == "app_registry_iam_user_projection":
            self.users.append(row)
            return
        if table_name == "app_registry_iam_permission_projection":
            self.permissions.append(row)
            return
        if table_name == "app_registry_iam_user_permission_projection":
            self.user_permissions.append(row)
            return
        if table_name == "app_registry_iam_page_projection":
            self.pages.append(row)
            return
        if table_name == "app_registry_iam_page_route_prefix_projection":
            self.route_prefixes.append(row)
            return
        raise AssertionError(table_name)

    def delete(self, row: object) -> None:
        for rows in (
            self.users,
            self.permissions,
            self.user_permissions,
            self.pages,
            self.route_prefixes,
        ):
            if row in rows:
                rows.remove(row)
                return

    def flush(self) -> None:
        assert self.run is not None
        self.run.id = 1

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        raise AssertionError("rollback should not be called")

    def refresh(self, row: object) -> None:
        self.refreshed = True


def _iam_snapshot_payload() -> dict[str, Any]:
    snapshot_at = datetime.now(UTC).isoformat()
    return {
        "app_code": "wms",
        "app_name": "仓储管理",
        "snapshot_at": snapshot_at,
        "users": [
            {
                "user_id": 1,
                "username": "admin",
                "is_active": True,
                "full_name": "管理员",
                "phone": None,
                "email": None,
            }
        ],
        "permissions": [
            {
                "permission_id": 10,
                "permission_code": "page.wms.read",
            }
        ],
        "user_permissions": [
            {
                "user_id": 1,
                "permission_id": 10,
                "permission_code": "page.wms.read",
                "granted_at": snapshot_at,
            }
        ],
        "page_registry": [
            {
                "page_code": "wms",
                "page_name": "仓储管理",
                "parent_page_code": None,
                "level": 1,
                "domain_code": "wms",
                "show_in_topbar": True,
                "show_in_sidebar": True,
                "inherit_permissions": False,
                "read_permission_code": "page.wms.read",
                "write_permission_code": "page.wms.write",
                "sort_order": 10,
                "is_active": True,
            }
        ],
        "page_route_prefixes": [
            {
                "id": 1,
                "page_code": "wms",
                "route_prefix": "/wms",
                "sort_order": 10,
                "is_active": True,
            }
        ],
    }


def test_system_iam_sync_run_contract_shape() -> None:
    checked_at = datetime.now(UTC)
    payload = SystemIamSyncRunOut.model_validate(
        {
            "id": 1,
            "app_code": "wms",
            "source_base_url": "http://127.0.0.1:8000",
            "status": "success",
            "started_at": checked_at,
            "finished_at": checked_at,
            "source_snapshot_at": checked_at,
            "fetched_count": 5,
            "inserted_count": 5,
            "updated_count": 0,
            "deleted_count": 0,
            "error_message": None,
            "raw_excerpt": None,
        }
    )

    assert payload.app_code == "wms"
    assert payload.status == "success"


def test_system_iam_snapshot_sync_service_writes_projection_rows() -> None:
    repo = FakeSyncRepo()
    fetched: list[tuple[str, dict[str, str]]] = []

    def fake_fetcher(
        url: str,
        timeout_seconds: float,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        assert timeout_seconds > 0
        fetched.append((url, dict(headers)))
        return _iam_snapshot_payload()

    service = SystemIamSnapshotSyncService(
        SimpleNamespace(),
        repository=repo,  # type: ignore[arg-type]
        json_fetcher=fake_fetcher,
    )

    result = service.sync_iam_snapshot("wms")

    assert result.status == "success"
    assert result.fetched_count == 5
    assert result.inserted_count == 5
    assert result.updated_count == 0
    assert result.deleted_count == 0

    assert fetched == [
        (
            f"http://127.0.0.1:8000{IAM_SNAPSHOT_PATH}",
            {"X-Service-Client": ERP_SERVICE_CLIENT},
        )
    ]

    assert repo.committed is True
    assert repo.refreshed is True

    assert repo.users[0].app_code == "wms"
    assert repo.users[0].source_user_id == 1
    assert repo.users[0].username == "admin"

    assert repo.permissions[0].permission_code == "page.wms.read"
    assert repo.user_permissions[0].permission_code == "page.wms.read"

    assert repo.pages[0].page_code == "wms"
    assert repo.pages[0].read_permission_code == "page.wms.read"

    assert repo.route_prefixes[0].route_prefix == "/wms"
