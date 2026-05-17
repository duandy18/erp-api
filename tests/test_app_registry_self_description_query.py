from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from app.app_registry.contracts.app_registry_self_description_contracts import (
    AppRegistrySelfDescriptionOut,
)
from app.app_registry.services.app_registry_self_description_service import (
    AppRegistrySelfDescriptionService,
)
from app.main import app


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
        self.app = SimpleNamespace(code="wms", name="仓储管理")
        self.manifest = SimpleNamespace(
            app_code="wms",
            app_name="仓储管理",
            app_type="business_system",
            status="available",
            description="WMS",
            default_web_path="/wms/",
            default_api_path="/api/wms",
            local_web_url="http://127.0.0.1:5173",
            local_api_url="http://127.0.0.1:8000",
            health_url="/healthz",
            db_health_url=None,
            openapi_url="/openapi.json",
            page_catalog_url="/system/read/v1/page-catalog",
            service_capabilities_url="/system/read/v1/service-capabilities",
            service_dependencies_url="/system/read/v1/service-dependencies",
            version="1.1.0",
            build_environment="dev",
            build_git_sha=None,
            build_time=None,
            last_synced_at=checked_at,
        )
        self.page = SimpleNamespace(
            page_code="wms",
            page_name="仓储管理",
            route_path="/wms",
            parent_page_code=None,
            level=1,
            read_permission_code="page.wms.read",
            write_permission_code="page.wms.write",
            is_active=True,
            sort_order=10,
            source_updated_at=None,
            last_synced_at=checked_at,
        )
        self.capability = SimpleNamespace(
            capability_code="wms.read.shipping_handoffs",
            capability_name="Read WMS shipping handoffs",
            resource_code="shipping_handoffs",
            permission_code="wms.read.shipping_handoffs",
            description="read handoffs",
            is_active=True,
            source_updated_at=checked_at,
            last_synced_at=checked_at,
        )
        self.capability_route = SimpleNamespace(
            capability_code="wms.read.shipping_handoffs",
            http_method="GET",
            path="/shipping-assist/handoffs/ready",
            route_name="list_ready_handoffs",
            auth_required=True,
            is_active=True,
            source_created_at=None,
            last_synced_at=checked_at,
        )
        self.dependency = SimpleNamespace(
            dependency_code="wms.depends_on.pms.items",
            dependency_name="PMS items",
            target_app_code="pms",
            target_capability_code="pms.read.items",
            required_permission_code="pms.read.items",
            description="read PMS items",
            is_required=True,
            is_active=True,
            required_config_keys=["PMS_API_BASE_URL"],
            source_modules=["app.integrations.pms.client"],
            last_synced_at=checked_at,
        )
        self.dependency_endpoint = SimpleNamespace(
            dependency_code="wms.depends_on.pms.items",
            http_method="GET",
            path="/pms/read/v1/projection-feed/items",
            purpose="sync PMS items",
            last_synced_at=checked_at,
        )
        self.sync_run = SimpleNamespace(
            id=1,
            app_code="wms",
            sync_type="all",
            source_base_url="http://127.0.0.1:8000",
            status="success",
            started_at=checked_at,
            finished_at=checked_at,
            fetched_count=98,
            inserted_count=98,
            updated_count=0,
            deleted_count=0,
            error_message=None,
            raw_excerpt=None,
        )

    def get_app(self, code: str):
        return self.app if code == "wms" else None

    def get_manifest(self, app_code: str):
        return self.manifest if app_code == "wms" else None

    def list_pages(self, app_code: str):
        return [self.page] if app_code == "wms" else []

    def list_capabilities(self, app_code: str):
        return [self.capability] if app_code == "wms" else []

    def list_capability_routes(self, app_code: str):
        return [self.capability_route] if app_code == "wms" else []

    def list_dependencies(self, source_app_code: str):
        return [self.dependency] if source_app_code == "wms" else []

    def list_dependency_endpoints(self, source_app_code: str):
        return [self.dependency_endpoint] if source_app_code == "wms" else []

    def get_latest_sync_run(self, app_code: str):
        return self.sync_run if app_code == "wms" else None


def test_app_registry_self_description_query_route_is_mounted() -> None:
    assert (
        "GET",
        "/admin/app-registry/apps/{code}/self-description",
    ) in _method_paths()


def test_app_registry_self_description_query_contract_shape() -> None:
    payload = AppRegistrySelfDescriptionOut.model_validate(
        {
            "app_code": "wms",
            "app_name": "仓储管理",
            "manifest": None,
            "pages": [],
            "capabilities": [],
            "dependencies": [],
            "latest_sync_run": None,
        }
    )

    assert payload.app_code == "wms"
    assert payload.manifest is None


def test_app_registry_self_description_service_builds_nested_payload() -> None:
    service = AppRegistrySelfDescriptionService(
        SimpleNamespace(),
        repository=FakeRepo(),  # type: ignore[arg-type]
    )

    payload = service.get_app_self_description("wms")

    assert payload.app_code == "wms"
    assert payload.app_name == "仓储管理"
    assert payload.manifest is not None
    assert payload.manifest.version == "1.1.0"
    assert len(payload.pages) == 1
    assert payload.pages[0].page_code == "wms"
    assert len(payload.capabilities) == 1
    assert payload.capabilities[0].capability_code == "wms.read.shipping_handoffs"
    assert payload.capabilities[0].routes[0].path == "/shipping-assist/handoffs/ready"
    assert len(payload.dependencies) == 1
    assert payload.dependencies[0].dependency_code == "wms.depends_on.pms.items"
    assert payload.dependencies[0].required_config_keys == ["PMS_API_BASE_URL"]
    assert payload.dependencies[0].endpoints[0].path == (
        "/pms/read/v1/projection-feed/items"
    )
    assert payload.latest_sync_run is not None
    assert payload.latest_sync_run.status == "success"
