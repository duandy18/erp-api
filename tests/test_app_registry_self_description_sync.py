from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from app.app_registry.contracts.app_registry_self_description_sync_contracts import (
    AppRegistrySelfDescriptionSyncRunOut,
)
from app.app_registry.services.app_registry_self_description_sync_service import (
    AppRegistrySelfDescriptionSyncService,
)
from app.main import app

HTTP_OK = 200


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
        self.app = SimpleNamespace(
            code="wms",
            local_api_url="http://127.0.0.1:8000/",
        )
        self.run: Any | None = None
        self.manifest: Any | None = None
        self.pages: list[Any] = []
        self.capabilities: list[Any] = []
        self.capability_routes: list[Any] = []
        self.dependencies: list[Any] = []
        self.dependency_endpoints: list[Any] = []
        self.committed = False
        self.refreshed = False

    def get_app(self, code: str) -> object | None:
        if code == "wms":
            return self.app
        return None

    def get_manifest_snapshot(self, app_code: str) -> object | None:
        return self.manifest if app_code == "wms" else None

    def list_page_catalog_pages(self, app_code: str) -> list[Any]:
        return list(self.pages) if app_code == "wms" else []

    def list_service_capabilities(self, app_code: str) -> list[Any]:
        return list(self.capabilities) if app_code == "wms" else []

    def list_service_capability_routes(self, app_code: str) -> list[Any]:
        return list(self.capability_routes) if app_code == "wms" else []

    def list_service_dependencies(self, source_app_code: str) -> list[Any]:
        return list(self.dependencies) if source_app_code == "wms" else []

    def list_service_dependency_endpoints(self, source_app_code: str) -> list[Any]:
        return list(self.dependency_endpoints) if source_app_code == "wms" else []

    def add(self, row: Any) -> None:
        table_name = row.__table__.name
        if table_name == "app_registry_self_description_sync_runs":
            self.run = row
            return
        if table_name == "app_registry_app_manifest_snapshots":
            self.manifest = row
            return
        if table_name == "app_registry_page_catalog_pages":
            self.pages.append(row)
            return
        if table_name == "app_registry_service_capability_catalog":
            self.capabilities.append(row)
            return
        if table_name == "app_registry_service_capability_routes":
            self.capability_routes.append(row)
            return
        if table_name == "app_registry_service_dependency_catalog":
            self.dependencies.append(row)
            return
        if table_name == "app_registry_service_dependency_endpoints":
            self.dependency_endpoints.append(row)
            return
        raise AssertionError(table_name)

    def delete(self, row: Any) -> None:
        for rows in (
            self.pages,
            self.capabilities,
            self.capability_routes,
            self.dependencies,
            self.dependency_endpoints,
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

    def refresh(self, row: Any) -> None:
        self.refreshed = True


def _fake_payload(path: str) -> dict[str, Any]:
    if path == "/system/read/v1/app-manifest":
        return {
            "app_code": "wms",
            "app_name": "仓储执行",
            "app_type": "business_system",
            "status": "available",
            "description": "WMS",
            "default_web_path": "/wms/",
            "default_api_path": "/api/wms",
            "local_web_url": "http://127.0.0.1:5173",
            "local_api_url": "http://127.0.0.1:8000",
            "health_url": "/healthz",
            "db_health_url": "/health/db",
            "openapi_url": "/openapi.json",
            "page_catalog_url": "/system/read/v1/page-catalog",
            "service_capabilities_url": "/system/read/v1/service-capabilities",
            "service_dependencies_url": "/system/read/v1/service-dependencies",
            "version": "0.1.0",
            "build_info": {
                "environment": "dev",
                "git_sha": "abc",
                "build_time": None,
            },
        }

    if path == "/system/read/v1/page-catalog":
        return {
            "app_code": "wms",
            "app_name": "仓储执行",
            "pages": [
                {
                    "page_code": "wms",
                    "page_name": "仓储执行",
                    "route_path": "/wms",
                    "parent_page_code": None,
                    "level": 1,
                    "read_permission_code": "page.wms.read",
                    "write_permission_code": "page.wms.write",
                    "is_active": True,
                    "sort_order": 10,
                    "source_updated_at": None,
                }
            ],
        }

    if path == "/system/read/v1/service-capabilities":
        return {
            "app_code": "wms",
            "app_name": "仓储执行",
            "capabilities": [
                {
                    "capability_code": "wms.read.shipping_handoffs",
                    "capability_name": "Read WMS shipping handoffs",
                    "resource_code": "shipping_handoffs",
                    "permission_code": "wms.read.shipping_handoffs",
                    "description": "read handoffs",
                    "is_active": True,
                    "source_updated_at": datetime.now(UTC).isoformat(),
                    "routes": [
                        {
                            "http_method": "GET",
                            "path": "/shipping-assist/handoffs/ready",
                            "route_name": "list_ready_handoffs",
                            "auth_required": True,
                            "is_active": True,
                            "source_created_at": None,
                        }
                    ],
                }
            ],
        }

    if path == "/system/read/v1/service-dependencies":
        return {
            "app_code": "wms",
            "app_name": "仓储执行",
            "source_service_client_code": "wms-service",
            "dependencies": [
                {
                    "dependency_code": "wms.depends_on.pms.items",
                    "dependency_name": "PMS items",
                    "target_app_code": "pms",
                    "target_capability_code": "pms.read.items",
                    "required_permission_code": "pms.read.items",
                    "description": "read PMS items",
                    "is_required": True,
                    "is_active": True,
                    "required_config_keys": ["PMS_API_BASE_URL"],
                    "source_modules": ["app.integrations.pms.client"],
                    "endpoints": [
                        {
                            "http_method": "GET",
                            "path": "/pms/read/v1/projection-feed/items",
                            "purpose": "sync PMS items",
                        }
                    ],
                }
            ],
        }

    raise AssertionError(path)


def test_app_registry_self_description_sync_route_is_mounted() -> None:
    assert (
        "POST",
        "/admin/app-registry/apps/{code}/sync-self-description",
    ) in _method_paths()


def test_app_registry_self_description_sync_run_contract_shape() -> None:
    payload = AppRegistrySelfDescriptionSyncRunOut.model_validate(
        {
            "id": 1,
            "app_code": "wms",
            "sync_type": "all",
            "source_base_url": "http://127.0.0.1:8000",
            "status": "success",
            "started_at": datetime.now(UTC),
            "finished_at": datetime.now(UTC),
            "fetched_count": 6,
            "inserted_count": 6,
            "updated_count": 0,
            "deleted_count": 0,
            "error_message": None,
            "raw_excerpt": None,
        }
    )

    assert payload.app_code == "wms"
    assert payload.status == "success"
    assert payload.fetched_count == 6


def test_app_registry_self_description_sync_service_writes_projection_rows() -> None:
    repo = FakeRepo()
    fetched_urls: list[str] = []

    def fake_fetcher(url: str, timeout_seconds: float) -> dict[str, Any]:
        assert timeout_seconds > 0
        fetched_urls.append(url)
        path = url.removeprefix("http://127.0.0.1:8000")
        return _fake_payload(path)

    service = AppRegistrySelfDescriptionSyncService(
        SimpleNamespace(),
        repository=repo,  # type: ignore[arg-type]
        json_fetcher=fake_fetcher,
    )

    result = service.sync_app_self_description("wms")

    assert result.status == "success"
    assert result.fetched_count == 6
    assert result.inserted_count == 6
    assert result.updated_count == 0
    assert result.deleted_count == 0

    assert fetched_urls == [
        "http://127.0.0.1:8000/system/read/v1/app-manifest",
        "http://127.0.0.1:8000/system/read/v1/page-catalog",
        "http://127.0.0.1:8000/system/read/v1/service-capabilities",
        "http://127.0.0.1:8000/system/read/v1/service-dependencies",
    ]

    assert repo.committed is True
    assert repo.refreshed is True
    assert repo.manifest.app_name == "仓储执行"
    assert repo.pages[0].page_code == "wms"
    assert repo.capabilities[0].capability_code == "wms.read.shipping_handoffs"
    assert repo.capability_routes[0].path == "/shipping-assist/handoffs/ready"
    assert repo.dependencies[0].dependency_code == "wms.depends_on.pms.items"
    assert repo.dependency_endpoints[0].path == "/pms/read/v1/projection-feed/items"
