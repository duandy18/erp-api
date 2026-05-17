from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter

from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryDependency,
    AppRegistryGatewayBinding,
    AppRegistryOpenApiSource,
    AppRegistryServiceClient,
    AppRegistryServicePermission,
)
from app.system_monitoring.contracts.system_monitoring_check_contracts import (
    JsonScalar,
    SystemMonitoringCheckResultOut,
    SystemMonitoringCheckTarget,
)
from app.system_monitoring.contracts.system_monitoring_contracts import SystemMonitoringStatus

MAX_OPENAPI_BYTES = 2_000_000
OPENAPI_FETCH_TIMEOUT_SECONDS = 5.0


class SystemMonitoringCheckNotFoundError(ValueError):
    pass


class SystemMonitoringOpenApiFetchError(RuntimeError):
    pass


class SystemMonitoringOpenApiSaveError(RuntimeError):
    pass


@dataclass(frozen=True)
class OpenApiFetchResult:
    http_status: int
    raw_text: str
    checksum: str
    latency_ms: int


def _latency_ms(started_perf: float) -> int:
    return max(0, int((perf_counter() - started_perf) * 1000))


def default_openapi_fetcher(
    url: str,
    timeout_seconds: float = OPENAPI_FETCH_TIMEOUT_SECONDS,
) -> OpenApiFetchResult:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "erp-control-plane-openapi-check/0.1"},
    )
    started_perf = perf_counter()

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read(MAX_OPENAPI_BYTES + 1)
            if len(raw) > MAX_OPENAPI_BYTES:
                raise SystemMonitoringOpenApiFetchError("OpenAPI 响应超过允许大小")

            return OpenApiFetchResult(
                http_status=int(response.getcode()),
                raw_text=raw.decode("utf-8", errors="replace"),
                checksum=hashlib.sha256(raw).hexdigest(),
                latency_ms=_latency_ms(started_perf),
            )
    except urllib.error.HTTPError as exc:
        message = f"OpenAPI 请求返回 HTTP {int(exc.code)}"
        raise SystemMonitoringOpenApiFetchError(message) from exc
    except urllib.error.URLError as exc:
        reason = str(exc.reason).strip() or "OpenAPI 请求失败"
        raise SystemMonitoringOpenApiFetchError(reason) from exc
    except TimeoutError as exc:
        raise SystemMonitoringOpenApiFetchError("OpenAPI 请求超时") from exc
    except (OSError, ValueError) as exc:
        message = str(exc).strip() or "OpenAPI 请求失败"
        raise SystemMonitoringOpenApiFetchError(message) from exc


def _result(
    *,
    target_type: SystemMonitoringCheckTarget,
    target_id: int,
    status: SystemMonitoringStatus,
    checked_at: datetime,
    message: str,
    details: dict[str, JsonScalar] | None = None,
) -> SystemMonitoringCheckResultOut:
    return SystemMonitoringCheckResultOut(
        target_type=target_type,
        target_id=target_id,
        status=status,
        checked_at=checked_at,
        message=message,
        details=details or {},
    )


def _app_exists(db: Session, app_code: object) -> bool:
    return db.get(AppRegistryApp, str(app_code)) is not None


def _validate_openapi_document(raw_text: str) -> None:
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise SystemMonitoringOpenApiFetchError("OpenAPI 响应不是合法 JSON") from exc

    if not isinstance(payload, dict):
        raise SystemMonitoringOpenApiFetchError("OpenAPI 响应不是 JSON 对象")

    if "openapi" not in payload and "swagger" not in payload:
        raise SystemMonitoringOpenApiFetchError("OpenAPI 响应缺少 openapi/swagger 字段")


class SystemMonitoringCheckService:
    def __init__(
        self,
        db: Session,
        *,
        openapi_fetcher=default_openapi_fetcher,
    ) -> None:
        self.db = db
        self.openapi_fetcher = openapi_fetcher

    def check_gateway_binding(self, binding_id: int) -> SystemMonitoringCheckResultOut:
        checked_at = datetime.now(UTC)
        row = self.db.get(AppRegistryGatewayBinding, binding_id)
        if row is None:
            raise SystemMonitoringCheckNotFoundError("Gateway 绑定不存在")

        details: dict[str, JsonScalar] = {
            "app_code": str(row.app_code),
            "env_code": str(row.env_code),
            "web_path": str(row.web_path),
            "api_path": str(row.api_path),
            "web_upstream_url": row.web_upstream_url,
            "api_upstream_url": row.api_upstream_url,
            "rewrite_mode": str(row.rewrite_mode),
            "is_published": bool(row.is_published),
            "is_active": bool(row.is_active),
        }

        if not row.is_active:
            return _result(
                target_type="gateway",
                target_id=binding_id,
                status="warning",
                checked_at=checked_at,
                message="Gateway 绑定未启用",
                details=details,
            )

        if not str(row.web_path).startswith("/") or not str(row.api_path).startswith("/"):
            return _result(
                target_type="gateway",
                target_id=binding_id,
                status="not_configured",
                checked_at=checked_at,
                message="Gateway Web/API 路径配置不完整",
                details=details,
            )

        if not row.web_upstream_url or not row.api_upstream_url:
            return _result(
                target_type="gateway",
                target_id=binding_id,
                status="not_configured",
                checked_at=checked_at,
                message="Gateway upstream 配置不完整",
                details=details,
            )

        if not row.is_published:
            return _result(
                target_type="gateway",
                target_id=binding_id,
                status="warning",
                checked_at=checked_at,
                message="Gateway 绑定未发布",
                details=details,
            )

        return _result(
            target_type="gateway",
            target_id=binding_id,
            status="ok",
            checked_at=checked_at,
            message="Gateway 绑定配置正常",
            details=details,
        )

    def check_dependency(self, dependency_id: int) -> SystemMonitoringCheckResultOut:
        checked_at = datetime.now(UTC)
        row = self.db.get(AppRegistryDependency, dependency_id)
        if row is None:
            raise SystemMonitoringCheckNotFoundError("系统依赖不存在")

        source_exists = _app_exists(self.db, row.source_app_code)
        target_exists = _app_exists(self.db, row.target_app_code)
        details: dict[str, JsonScalar] = {
            "source_app_code": str(row.source_app_code),
            "target_app_code": str(row.target_app_code),
            "dependency_type": str(row.dependency_type),
            "dependency_status": str(row.status),
            "is_required": bool(row.is_required),
            "is_active": bool(row.is_active),
            "source_exists": source_exists,
            "target_exists": target_exists,
        }

        if not source_exists or not target_exists:
            return _result(
                target_type="dependency",
                target_id=dependency_id,
                status="error",
                checked_at=checked_at,
                message="系统依赖引用的来源或目标应用不存在",
                details=details,
            )

        if not row.is_active:
            return _result(
                target_type="dependency",
                target_id=dependency_id,
                status="warning",
                checked_at=checked_at,
                message="系统依赖未启用",
                details=details,
            )

        status = str(row.status)
        if status == "ready":
            return _result(
                target_type="dependency",
                target_id=dependency_id,
                status="ok",
                checked_at=checked_at,
                message="系统依赖已就绪",
                details=details,
            )

        if status == "planned":
            return _result(
                target_type="dependency",
                target_id=dependency_id,
                status="unchecked",
                checked_at=checked_at,
                message="系统依赖仍处于计划状态",
                details=details,
            )

        return _result(
            target_type="dependency",
            target_id=dependency_id,
            status="warning",
            checked_at=checked_at,
            message="系统依赖状态待处理",
            details=details,
        )

    def check_service_client(self, client_id: int) -> SystemMonitoringCheckResultOut:
        checked_at = datetime.now(UTC)
        row = self.db.get(AppRegistryServiceClient, client_id)
        if row is None:
            raise SystemMonitoringCheckNotFoundError("Service Client 不存在")

        app_exists = _app_exists(self.db, row.app_code)
        details: dict[str, JsonScalar] = {
            "app_code": str(row.app_code),
            "client_code": str(row.client_code),
            "auth_type": str(row.auth_type),
            "secret_ref": row.secret_ref,
            "is_active": bool(row.is_active),
            "app_exists": app_exists,
        }

        if not app_exists:
            return _result(
                target_type="service_client",
                target_id=client_id,
                status="error",
                checked_at=checked_at,
                message="Service Client 所属应用不存在",
                details=details,
            )

        if not row.is_active:
            return _result(
                target_type="service_client",
                target_id=client_id,
                status="warning",
                checked_at=checked_at,
                message="Service Client 未启用",
                details=details,
            )

        return _result(
            target_type="service_client",
            target_id=client_id,
            status="ok",
            checked_at=checked_at,
            message="Service Client 配置正常",
            details=details,
        )

    def check_service_permission(self, permission_id: int) -> SystemMonitoringCheckResultOut:
        checked_at = datetime.now(UTC)
        row = self.db.get(AppRegistryServicePermission, permission_id)
        if row is None:
            raise SystemMonitoringCheckNotFoundError("Service Permission 不存在")

        client = self.db.get(AppRegistryServiceClient, int(row.client_id))
        source_exists = _app_exists(self.db, row.source_app_code)
        target_exists = _app_exists(self.db, row.target_app_code)
        client_matches_source = (
            client is not None and str(client.app_code) == str(row.source_app_code)
        )

        details: dict[str, JsonScalar] = {
            "client_id": int(row.client_id),
            "client_code": str(client.client_code) if client is not None else None,
            "source_app_code": str(row.source_app_code),
            "target_app_code": str(row.target_app_code),
            "permission_code": str(row.permission_code),
            "is_active": bool(row.is_active),
            "client_exists": client is not None,
            "source_exists": source_exists,
            "target_exists": target_exists,
            "client_matches_source": client_matches_source,
        }

        if client is None or not source_exists or not target_exists:
            return _result(
                target_type="service_permission",
                target_id=permission_id,
                status="error",
                checked_at=checked_at,
                message="Service Permission 引用关系不完整",
                details=details,
            )

        if not client_matches_source:
            return _result(
                target_type="service_permission",
                target_id=permission_id,
                status="warning",
                checked_at=checked_at,
                message="Service Permission 的 client 与来源系统不一致",
                details=details,
            )

        if not client.is_active:
            return _result(
                target_type="service_permission",
                target_id=permission_id,
                status="warning",
                checked_at=checked_at,
                message="关联 Service Client 未启用",
                details=details,
            )

        if not row.is_active:
            return _result(
                target_type="service_permission",
                target_id=permission_id,
                status="warning",
                checked_at=checked_at,
                message="Service Permission 未启用",
                details=details,
            )

        return _result(
            target_type="service_permission",
            target_id=permission_id,
            status="ok",
            checked_at=checked_at,
            message="Service Permission 配置正常",
            details=details,
        )

    def check_openapi_source(self, source_id: int) -> SystemMonitoringCheckResultOut:
        checked_at = datetime.now(UTC)
        row = self.db.get(AppRegistryOpenApiSource, source_id)
        if row is None:
            raise SystemMonitoringCheckNotFoundError("OpenAPI 来源不存在")

        details: dict[str, JsonScalar] = {
            "app_code": str(row.app_code),
            "env_code": str(row.env_code),
            "endpoint_id": int(row.endpoint_id),
            "openapi_url": str(row.openapi_url),
            "is_active": bool(row.is_active),
        }

        if not row.is_active:
            return _result(
                target_type="openapi",
                target_id=source_id,
                status="warning",
                checked_at=checked_at,
                message="OpenAPI 来源未启用",
                details=details,
            )

        try:
            fetch_result = self.openapi_fetcher(str(row.openapi_url), OPENAPI_FETCH_TIMEOUT_SECONDS)
            _validate_openapi_document(fetch_result.raw_text)
        except SystemMonitoringOpenApiFetchError as exc:
            row.last_fetched_at = checked_at
            row.last_status = "failure"
            row.updated_at = checked_at
            self._commit_openapi_result()
            return _result(
                target_type="openapi",
                target_id=source_id,
                status="error",
                checked_at=checked_at,
                message=str(exc),
                details=details,
            )

        row.last_fetched_at = checked_at
        row.last_checksum = str(fetch_result.checksum)
        row.last_status = "success"
        row.updated_at = checked_at
        self._commit_openapi_result()

        details.update(
            {
                "http_status": int(fetch_result.http_status),
                "latency_ms": int(fetch_result.latency_ms),
                "checksum": str(fetch_result.checksum),
            }
        )

        return _result(
            target_type="openapi",
            target_id=source_id,
            status="ok",
            checked_at=checked_at,
            message="OpenAPI 拉取成功",
            details=details,
        )

    def _commit_openapi_result(self) -> None:
        try:
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            raise SystemMonitoringOpenApiSaveError("OpenAPI 检查结果保存失败") from exc


__all__ = [
    "OpenApiFetchResult",
    "SystemMonitoringCheckNotFoundError",
    "SystemMonitoringCheckService",
    "SystemMonitoringOpenApiFetchError",
    "SystemMonitoringOpenApiSaveError",
    "default_openapi_fetcher",
]
