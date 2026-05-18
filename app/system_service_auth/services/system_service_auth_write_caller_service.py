from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_app_metadata import (
    AppRegistryServiceClient,
    AppRegistryServicePermission,
    AppRegistryServicePermissionWriteRun,
)
from app.system_service_auth.contracts.system_service_auth_write_status_contracts import (
    SystemServiceAuthWriteRunOut,
)
from app.system_service_auth.repositories.system_service_auth_write_caller_repository import (
    SystemServiceAuthWriteCallerRepository,
)

HTTP_TIMEOUT_SECONDS = 5.0
MAX_RAW_EXCERPT_LENGTH = 2048
MAX_TARGET_DESCRIPTION_LENGTH = 255
ERP_SERVICE_CLIENT_CODE = "erp-service"
SERVICE_PERMISSION_APPLY_PATH = "/system/write/v1/service-permissions/apply"
SERVICE_PERMISSION_VERIFY_PATH = "/system/write/v1/service-permissions/verify"


class SystemServiceAuthWritePermissionNotFoundError(ValueError):
    pass


class SystemServiceAuthWriteClientNotFoundError(ValueError):
    pass


class SystemServiceAuthWriteTargetAppNotFoundError(ValueError):
    pass


class SystemServiceAuthWriteTargetConfigError(ValueError):
    pass


class SystemServiceAuthWriteTargetFetchError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        http_status: int | None = None,
        raw_excerpt: str | None = None,
    ) -> None:
        super().__init__(message)
        self.http_status = http_status
        self.raw_excerpt = raw_excerpt


class SystemServiceAuthWriteTargetPayloadError(ValueError):
    pass


@dataclass(frozen=True)
class TargetServiceHttpResult:
    http_status: int
    payload: dict[str, Any]
    raw_excerpt: str | None


TargetJsonRequest = Callable[
    [str, str, Mapping[str, str], Mapping[str, Any] | None, float],
    TargetServiceHttpResult,
]


def _limit(value: str | None, max_length: int = MAX_RAW_EXCERPT_LENGTH) -> str | None:
    if value is None:
        return None
    if len(value) <= max_length:
        return value
    return value[:max_length]


def _decode_excerpt(raw: bytes) -> str | None:
    if not raw:
        return None

    text = raw.decode("utf-8", errors="replace").strip()
    return _limit(text) if text else None


def default_target_json_request(
    method: str,
    url: str,
    headers: Mapping[str, str],
    body: Mapping[str, Any] | None,
    timeout_seconds: float,
) -> TargetServiceHttpResult:
    normalized_method = method.upper()
    data = None
    request_headers = {
        "User-Agent": "erp-control-plane-service-auth-write/0.1",
        **dict(headers),
    }

    if body is not None:
        data = json.dumps(dict(body)).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        url,
        data=data,
        method=normalized_method,
        headers=request_headers,
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read(MAX_RAW_EXCERPT_LENGTH * 8)
            text = raw.decode("utf-8", errors="replace")
            http_status = int(response.getcode())
    except urllib.error.HTTPError as exc:
        raw_excerpt = _decode_excerpt(exc.read(MAX_RAW_EXCERPT_LENGTH * 4))
        message = f"目标系统调用失败: HTTP {int(exc.code)} {url}"
        if raw_excerpt:
            message = f"{message}: {raw_excerpt}"
        raise SystemServiceAuthWriteTargetFetchError(
            message,
            http_status=int(exc.code),
            raw_excerpt=raw_excerpt,
        ) from exc
    except TimeoutError as exc:
        raise SystemServiceAuthWriteTargetFetchError(f"目标系统调用超时: {url}") from exc
    except urllib.error.URLError as exc:
        raise SystemServiceAuthWriteTargetFetchError(
            f"目标系统调用失败: {str(exc.reason)}"
        ) from exc
    except OSError as exc:
        raise SystemServiceAuthWriteTargetFetchError(f"目标系统调用失败: {exc}") from exc

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemServiceAuthWriteTargetPayloadError(
            f"目标系统返回非 JSON: {url}"
        ) from exc

    if not isinstance(payload, dict):
        raise SystemServiceAuthWriteTargetPayloadError(
            f"目标系统返回结构不是对象: {url}"
        )

    return TargetServiceHttpResult(
        http_status=http_status,
        payload=payload,
        raw_excerpt=_decode_excerpt(text.encode("utf-8")),
    )


def _join_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


def _run_out(row: AppRegistryServicePermissionWriteRun) -> SystemServiceAuthWriteRunOut:
    return SystemServiceAuthWriteRunOut(
        run_id=int(row.id),
        permission_id=int(row.permission_id),
        source_app_code=str(row.source_app_code),
        target_app_code=str(row.target_app_code),
        client_code=row.client_code,
        permission_code=str(row.permission_code),
        operation=str(row.operation),
        status=str(row.status),
        started_at=row.started_at,
        finished_at=row.finished_at,
        target_base_url=row.target_base_url,
        http_status=row.http_status,
        error_message=row.error_message,
        raw_excerpt=row.raw_excerpt,
    )


def _required_str(payload: Mapping[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise SystemServiceAuthWriteTargetPayloadError(f"{field_name} 必须是非空字符串")
    return value.strip()


def _required_bool(payload: Mapping[str, Any], field_name: str) -> bool:
    value = payload.get(field_name)
    if not isinstance(value, bool):
        raise SystemServiceAuthWriteTargetPayloadError(f"{field_name} 必须是布尔值")
    return value


@dataclass(frozen=True)
class PermissionWriteContext:
    permission: AppRegistryServicePermission
    client: AppRegistryServiceClient
    target_app: AppRegistryApp
    target_base_url: str


class SystemServiceAuthWriteCallerService:
    def __init__(
        self,
        db: Session,
        *,
        repository: SystemServiceAuthWriteCallerRepository | None = None,
        target_request: TargetJsonRequest = default_target_json_request,
    ) -> None:
        self.repo = repository or SystemServiceAuthWriteCallerRepository(db)
        self.target_request = target_request

    def apply_permission(self, permission_id: int) -> SystemServiceAuthWriteRunOut:
        context = self._load_context(permission_id)
        operation = "upsert" if bool(context.permission.is_active) else "disable"
        run = self._create_run(context, operation=operation)

        try:
            result = self._call_target_apply(context)
            self._assert_apply_payload_matches_context(result.payload, context)
        except (
            SystemServiceAuthWriteTargetFetchError,
            SystemServiceAuthWriteTargetPayloadError,
        ) as exc:
            self._mark_run_failure(run, exc)
            return _run_out(run)

        self._mark_run_success(run, result)
        return _run_out(run)

    def verify_permission(self, permission_id: int) -> SystemServiceAuthWriteRunOut:
        context = self._load_context(permission_id)
        run = self._create_run(context, operation="verify")

        try:
            result = self._call_target_verify(context)
            self._assert_verify_payload_matches_context(result.payload, context)
        except (
            SystemServiceAuthWriteTargetFetchError,
            SystemServiceAuthWriteTargetPayloadError,
        ) as exc:
            self._mark_run_failure(run, exc)
            return _run_out(run)

        self._mark_run_success(run, result)
        return _run_out(run)

    def _load_context(self, permission_id: int) -> PermissionWriteContext:
        permission = self.repo.get_permission(permission_id)
        if permission is None:
            raise SystemServiceAuthWritePermissionNotFoundError("系统调用授权不存在")

        client = self.repo.get_client(int(permission.client_id))
        if client is None:
            raise SystemServiceAuthWriteClientNotFoundError("service client 不存在")

        target_app = self.repo.get_app(str(permission.target_app_code))
        if target_app is None:
            raise SystemServiceAuthWriteTargetAppNotFoundError("目标系统应用不存在")

        target_base_url = str(target_app.local_api_url or "").strip().rstrip("/")
        if not target_base_url.startswith(("http://", "https://")):
            raise SystemServiceAuthWriteTargetConfigError("目标系统 local_api_url 不合法")

        return PermissionWriteContext(
            permission=permission,
            client=client,
            target_app=target_app,
            target_base_url=target_base_url,
        )

    def _create_run(
        self,
        context: PermissionWriteContext,
        *,
        operation: str,
    ) -> AppRegistryServicePermissionWriteRun:
        run = AppRegistryServicePermissionWriteRun(
            permission_id=int(context.permission.id),
            source_app_code=str(context.permission.source_app_code),
            target_app_code=str(context.permission.target_app_code),
            client_code=str(context.client.client_code),
            permission_code=str(context.permission.permission_code),
            operation=operation,
            status="running",
            started_at=datetime.now(UTC),
            target_base_url=context.target_base_url,
        )
        self.repo.add(run)
        self.repo.flush()
        return run

    def _call_target_apply(
        self,
        context: PermissionWriteContext,
    ) -> TargetServiceHttpResult:
        description = str(context.permission.description).strip()
        body = {
            "client_code": str(context.client.client_code),
            "client_name": str(context.client.client_name),
            "capability_code": str(context.permission.permission_code),
            "description": _limit(description, MAX_TARGET_DESCRIPTION_LENGTH),
            "is_active": bool(context.permission.is_active),
        }

        return self.target_request(
            "POST",
            _join_url(context.target_base_url, SERVICE_PERMISSION_APPLY_PATH),
            {"X-Service-Client": ERP_SERVICE_CLIENT_CODE},
            body,
            HTTP_TIMEOUT_SECONDS,
        )

    def _call_target_verify(
        self,
        context: PermissionWriteContext,
    ) -> TargetServiceHttpResult:
        query = urllib.parse.urlencode(
            {
                "client_code": str(context.client.client_code),
                "capability_code": str(context.permission.permission_code),
            }
        )

        return self.target_request(
            "GET",
            f"{_join_url(context.target_base_url, SERVICE_PERMISSION_VERIFY_PATH)}?{query}",
            {"X-Service-Client": ERP_SERVICE_CLIENT_CODE},
            None,
            HTTP_TIMEOUT_SECONDS,
        )

    @staticmethod
    def _assert_apply_payload_matches_context(
        payload: Mapping[str, Any],
        context: PermissionWriteContext,
    ) -> None:
        expected_active = bool(context.permission.is_active)

        if _required_str(payload, "app_code") != str(context.permission.target_app_code):
            raise SystemServiceAuthWriteTargetPayloadError("目标系统 app_code 不一致")
        if _required_str(payload, "client_code") != str(context.client.client_code):
            raise SystemServiceAuthWriteTargetPayloadError("目标系统 client_code 不一致")
        if _required_str(payload, "capability_code") != str(context.permission.permission_code):
            raise SystemServiceAuthWriteTargetPayloadError("目标系统 capability_code 不一致")
        if _required_bool(payload, "applied") is not True:
            raise SystemServiceAuthWriteTargetPayloadError("目标系统未确认 applied")
        if _required_bool(payload, "is_active") is not expected_active:
            raise SystemServiceAuthWriteTargetPayloadError("目标系统 is_active 与 ERP 不一致")
        if _required_bool(payload, "verified") is not expected_active:
            raise SystemServiceAuthWriteTargetPayloadError("目标系统 verified 与 ERP 不一致")

    @staticmethod
    def _assert_verify_payload_matches_context(
        payload: Mapping[str, Any],
        context: PermissionWriteContext,
    ) -> None:
        expected_active = bool(context.permission.is_active)

        if _required_str(payload, "app_code") != str(context.permission.target_app_code):
            raise SystemServiceAuthWriteTargetPayloadError("目标系统 app_code 不一致")
        if _required_str(payload, "client_code") != str(context.client.client_code):
            raise SystemServiceAuthWriteTargetPayloadError("目标系统 client_code 不一致")
        if _required_str(payload, "capability_code") != str(context.permission.permission_code):
            raise SystemServiceAuthWriteTargetPayloadError("目标系统 capability_code 不一致")

        for field_name in ("client_exists", "capability_exists", "permission_exists"):
            if _required_bool(payload, field_name) is not True:
                raise SystemServiceAuthWriteTargetPayloadError(f"目标系统 {field_name} 不成立")

        if _required_bool(payload, "permission_is_active") is not expected_active:
            raise SystemServiceAuthWriteTargetPayloadError(
                "目标系统 permission_is_active 与 ERP 不一致"
            )
        if _required_bool(payload, "verified") is not expected_active:
            raise SystemServiceAuthWriteTargetPayloadError("目标系统 verified 与 ERP 不一致")

    def _mark_run_success(
        self,
        run: AppRegistryServicePermissionWriteRun,
        result: TargetServiceHttpResult,
    ) -> None:
        run.status = "success"
        run.finished_at = datetime.now(UTC)
        run.http_status = int(result.http_status)
        run.error_message = None
        run.raw_excerpt = _limit(result.raw_excerpt)
        self.repo.commit()
        self.repo.refresh(run)

    def _mark_run_failure(
        self,
        run: AppRegistryServicePermissionWriteRun,
        exc: Exception,
    ) -> None:
        run.status = "failure"
        run.finished_at = datetime.now(UTC)
        run.error_message = _limit(str(exc))
        run.raw_excerpt = getattr(exc, "raw_excerpt", None)
        run.http_status = getattr(exc, "http_status", None)
        self.repo.commit()
        self.repo.refresh(run)


__all__ = [
    "ERP_SERVICE_CLIENT_CODE",
    "SERVICE_PERMISSION_APPLY_PATH",
    "SERVICE_PERMISSION_VERIFY_PATH",
    "SystemServiceAuthWriteCallerService",
    "SystemServiceAuthWriteClientNotFoundError",
    "SystemServiceAuthWritePermissionNotFoundError",
    "SystemServiceAuthWriteTargetAppNotFoundError",
    "SystemServiceAuthWriteTargetConfigError",
    "SystemServiceAuthWriteTargetFetchError",
    "SystemServiceAuthWriteTargetPayloadError",
    "TargetServiceHttpResult",
    "default_target_json_request",
]
