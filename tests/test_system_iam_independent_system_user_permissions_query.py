from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from app.main import app
from app.system_iam.contracts import IndependentSystemUserPermissionsOut
from app.system_iam.services import IndependentSystemUserPermissionsService


def _method_paths() -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", None) or []
        for method in methods:
            if method in {"GET", "POST", "PATCH", "PUT", "DELETE"}:
                pairs.add((method, path))
    return pairs


class FakeRepo:
    def __init__(self) -> None:
        checked_at = datetime.now(UTC)
        self.app = SimpleNamespace(
            code="wms",
            name="仓储管理",
            app_type="business",
            status="ready",
            is_active=True,
        )
        self.run = SimpleNamespace(
            id=1,
            app_code="wms",
            source_base_url="http://127.0.0.1:8000",
            status="success",
            started_at=checked_at,
            finished_at=checked_at,
            source_snapshot_at=checked_at,
            fetched_count=8,
            inserted_count=8,
            updated_count=0,
            deleted_count=0,
            error_message=None,
            raw_excerpt=None,
        )
        self.user = SimpleNamespace(
            app_code="wms",
            source_user_id=1,
            username="admin",
            is_active=True,
            full_name="管理员",
            phone=None,
            email=None,
            last_synced_at=checked_at,
        )
        self.permission = SimpleNamespace(
            app_code="wms",
            source_permission_id=10,
            permission_code="page.wms.read",
            last_synced_at=checked_at,
        )
        self.user_permission = SimpleNamespace(
            app_code="wms",
            source_user_id=1,
            source_permission_id=10,
            permission_code="page.wms.read",
            granted_at=checked_at,
            last_synced_at=checked_at,
        )
        self.page = SimpleNamespace(
            app_code="wms",
            page_code="wms",
            page_name="仓储管理",
            parent_page_code=None,
            level=1,
            domain_code="wms",
            show_in_topbar=True,
            show_in_sidebar=True,
            inherit_permissions=False,
            read_permission_code="page.wms.read",
            write_permission_code="page.wms.write",
            sort_order=10,
            is_active=True,
            last_synced_at=checked_at,
        )
        self.route = SimpleNamespace(
            app_code="wms",
            page_code="wms",
            route_prefix="/wms",
            sort_order=10,
            is_active=True,
            last_synced_at=checked_at,
        )

    def list_apps(self, app_code: str | None = None):
        return [self.app] if app_code in {None, "wms"} else []

    def list_latest_sync_runs(self, app_codes: list[str]):
        return [self.run] if app_codes == ["wms"] else []

    def list_users(self, app_codes: list[str]):
        return [self.user] if app_codes == ["wms"] else []

    def list_permissions(self, app_codes: list[str]):
        return [self.permission] if app_codes == ["wms"] else []

    def list_user_permissions(self, app_codes: list[str]):
        return [self.user_permission] if app_codes == ["wms"] else []

    def list_pages(self, app_codes: list[str]):
        return [self.page] if app_codes == ["wms"] else []

    def list_route_prefixes(self, app_codes: list[str]):
        return [self.route] if app_codes == ["wms"] else []


def test_system_iam_independent_system_user_permissions_route_is_mounted() -> None:
    assert (
        "GET",
        "/admin/system-iam/independent-system-user-permissions",
    ) in _method_paths()


def test_system_iam_independent_system_user_permissions_contract_shape() -> None:
    payload = IndependentSystemUserPermissionsOut.model_validate(
        {
            "apps": [],
            "users": [],
            "permissions": [],
            "user_permissions": [],
            "page_registry": [],
            "page_route_prefixes": [],
            "latest_sync_runs": [],
        }
    )

    assert payload.apps == []
    assert payload.users == []


def test_system_iam_independent_system_user_permissions_service_builds_payload() -> None:
    service = IndependentSystemUserPermissionsService(
        SimpleNamespace(),
        repository=FakeRepo(),  # type: ignore[arg-type]
    )

    result = service.list_independent_system_user_permissions(app_code="wms")

    assert result.apps[0].app_code == "wms"
    assert result.latest_sync_runs[0].status == "success"

    assert result.users[0].source_user_id == 1
    assert result.users[0].username == "admin"

    assert result.permissions[0].permission_code == "page.wms.read"
    assert result.user_permissions[0].permission_code == "page.wms.read"

    assert result.page_registry[0].page_code == "wms"
    assert result.page_registry[0].read_permission_code == "page.wms.read"

    assert result.page_route_prefixes[0].route_prefix == "/wms"
