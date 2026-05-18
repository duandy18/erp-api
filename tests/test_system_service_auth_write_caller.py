from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from app.main import app
from app.system_service_auth.services.system_service_auth_write_caller_service import (
    ERP_SERVICE_CLIENT_CODE,
    SERVICE_PERMISSION_APPLY_PATH,
    SERVICE_PERMISSION_VERIFY_PATH,
    SystemServiceAuthWriteCallerService,
    TargetServiceHttpResult,
)

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


class FakeWriteCallerRepo:
    def __init__(self, *, permission_active: bool = True) -> None:
        now = datetime.now(UTC)
        self.permission = SimpleNamespace(
            id=1,
            client_id=9,
            source_app_code="wms",
            target_app_code="pms",
            permission_code="pms.read.items",
            description="WMS 读取 PMS 商品主数据",
            is_active=permission_active,
            created_at=now,
            updated_at=now,
        )
        self.client = SimpleNamespace(
            id=9,
            app_code="wms",
            client_code="wms-service",
            client_name="WMS Service Client",
            is_active=True,
        )
        self.target_app = SimpleNamespace(
            code="pms",
            name="PMS 商品主数据系统",
            local_api_url="http://127.0.0.1:8005/",
        )
        self.run: Any | None = None
        self.committed = False
        self.refreshed = False

    def get_permission(self, permission_id: int):
        return self.permission if permission_id == 1 else None

    def get_client(self, client_id: int):
        return self.client if client_id == 9 else None

    def get_app(self, app_code: str):
        return self.target_app if app_code == "pms" else None

    def add(self, row: object) -> None:
        self.run = row

    def flush(self) -> None:
        assert self.run is not None
        self.run.id = 88

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        raise AssertionError("rollback should not be called")

    def refresh(self, row: object) -> None:
        self.refreshed = True


def test_system_service_auth_write_caller_routes_are_mounted() -> None:
    pairs = _method_paths()

    assert ("POST", "/admin/system-service-auth/permissions/{permission_id}/apply") in pairs
    assert ("POST", "/admin/system-service-auth/permissions/{permission_id}/verify") in pairs


def test_system_service_auth_write_caller_apply_posts_to_target_write_v1() -> None:
    repo = FakeWriteCallerRepo()
    calls: list[tuple[str, str, dict[str, str], dict[str, Any] | None]] = []

    def fake_request(
        method: str,
        url: str,
        headers: dict[str, str],
        body: dict[str, Any] | None,
        timeout_seconds: float,
    ) -> TargetServiceHttpResult:
        assert timeout_seconds > 0
        calls.append((method, url, dict(headers), body))
        return TargetServiceHttpResult(
            http_status=HTTP_OK,
            payload={
                "app_code": "pms",
                "client_code": "wms-service",
                "client_name": "WMS Service Client",
                "capability_code": "pms.read.items",
                "description": "WMS 读取 PMS 商品主数据",
                "is_active": True,
                "applied": True,
                "verified": True,
                "permission_id": 12,
                "granted_at": datetime.now(UTC).isoformat(),
            },
            raw_excerpt='{"verified":true}',
        )

    service = SystemServiceAuthWriteCallerService(
        SimpleNamespace(),
        repository=repo,  # type: ignore[arg-type]
        target_request=fake_request,
    )

    result = service.apply_permission(1)

    assert result.run_id == 88
    assert result.operation == "upsert"
    assert result.status == "success"
    assert result.http_status == HTTP_OK
    assert result.target_base_url == "http://127.0.0.1:8005"
    assert repo.committed is True
    assert repo.refreshed is True

    assert calls == [
        (
            "POST",
            f"http://127.0.0.1:8005{SERVICE_PERMISSION_APPLY_PATH}",
            {"X-Service-Client": ERP_SERVICE_CLIENT_CODE},
            {
                "client_code": "wms-service",
                "client_name": "WMS Service Client",
                "capability_code": "pms.read.items",
                "description": "WMS 读取 PMS 商品主数据",
                "is_active": True,
            },
        )
    ]


def test_system_service_auth_write_caller_verify_gets_target_write_v1() -> None:
    repo = FakeWriteCallerRepo()
    calls: list[tuple[str, str, dict[str, str], dict[str, Any] | None]] = []

    def fake_request(
        method: str,
        url: str,
        headers: dict[str, str],
        body: dict[str, Any] | None,
        timeout_seconds: float,
    ) -> TargetServiceHttpResult:
        assert timeout_seconds > 0
        calls.append((method, url, dict(headers), body))
        return TargetServiceHttpResult(
            http_status=HTTP_OK,
            payload={
                "app_code": "pms",
                "client_code": "wms-service",
                "capability_code": "pms.read.items",
                "client_exists": True,
                "capability_exists": True,
                "permission_exists": True,
                "client_is_active": True,
                "capability_is_active": True,
                "permission_is_active": True,
                "description": "WMS 读取 PMS 商品主数据",
                "verified": True,
                "permission_id": 12,
                "granted_at": datetime.now(UTC).isoformat(),
            },
            raw_excerpt='{"verified":true}',
        )

    service = SystemServiceAuthWriteCallerService(
        SimpleNamespace(),
        repository=repo,  # type: ignore[arg-type]
        target_request=fake_request,
    )

    result = service.verify_permission(1)

    assert result.run_id == 88
    assert result.operation == "verify"
    assert result.status == "success"
    assert result.http_status == HTTP_OK

    assert calls == [
        (
            "GET",
            (
                f"http://127.0.0.1:8005{SERVICE_PERMISSION_VERIFY_PATH}"
                "?client_code=wms-service&capability_code=pms.read.items"
            ),
            {"X-Service-Client": ERP_SERVICE_CLIENT_CODE},
            None,
        )
    ]


def test_system_service_auth_write_caller_records_failure_when_target_mismatches() -> None:
    repo = FakeWriteCallerRepo(permission_active=True)

    def fake_request(
        method: str,
        url: str,
        headers: dict[str, str],
        body: dict[str, Any] | None,
        timeout_seconds: float,
    ) -> TargetServiceHttpResult:
        return TargetServiceHttpResult(
            http_status=HTTP_OK,
            payload={
                "app_code": "pms",
                "client_code": "wms-service",
                "capability_code": "pms.read.items",
                "client_exists": True,
                "capability_exists": True,
                "permission_exists": True,
                "client_is_active": True,
                "capability_is_active": True,
                "permission_is_active": False,
                "description": "WMS 读取 PMS 商品主数据",
                "verified": False,
                "permission_id": 12,
                "granted_at": datetime.now(UTC).isoformat(),
            },
            raw_excerpt='{"verified":false}',
        )

    service = SystemServiceAuthWriteCallerService(
        SimpleNamespace(),
        repository=repo,  # type: ignore[arg-type]
        target_request=fake_request,
    )

    result = service.verify_permission(1)

    assert result.run_id == 88
    assert result.operation == "verify"
    assert result.status == "failure"
    assert result.http_status is None
    assert "permission_is_active" in str(result.error_message)
