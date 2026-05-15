from __future__ import annotations

import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter

from sqlalchemy.orm import Session

from app.app_registry.contracts.app_registry_runtime_governance_contracts import (
    AppRegistryHealthCheckRunOut,
)
from app.app_registry.models.app_registry_system_metadata import (
    AppRegistryEndpoint,
    AppRegistryHealthCheck,
    AppRegistryHealthCheckRun,
)
from app.app_registry.repositories.app_registry_runtime_governance_repository import (
    AppRegistryRuntimeGovernanceRepository,
    AppRegistryRuntimeGovernanceSaveError,
)

MAX_MESSAGE_LENGTH = 512
MAX_RAW_EXCERPT_LENGTH = 2048


class AppRegistryHealthCheckNotFoundError(ValueError):
    pass


class AppRegistryHealthCheckInactiveError(ValueError):
    pass


class AppRegistryHealthCheckUnsupportedError(ValueError):
    pass


class HealthCheckHttpTimeoutError(TimeoutError):
    pass


class HealthCheckHttpRequestError(RuntimeError):
    pass


@dataclass(frozen=True)
class HttpStatusProbeResult:
    http_status: int
    raw_excerpt: str | None


HttpStatusProbe = Callable[[str, float], HttpStatusProbeResult]


def _limit(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    return value[:max_length]


def _decode_excerpt(raw: bytes) -> str | None:
    if not raw:
        return None

    text = raw.decode("utf-8", errors="replace").strip()
    if not text:
        return None

    return _limit(text, MAX_RAW_EXCERPT_LENGTH)


def default_http_status_probe(url: str, timeout_seconds: float) -> HttpStatusProbeResult:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "erp-control-plane-health-check/0.1"},
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read(MAX_RAW_EXCERPT_LENGTH)
            return HttpStatusProbeResult(
                http_status=int(response.getcode()),
                raw_excerpt=_decode_excerpt(raw),
            )
    except urllib.error.HTTPError as exc:
        raw = exc.read(MAX_RAW_EXCERPT_LENGTH)
        return HttpStatusProbeResult(
            http_status=int(exc.code),
            raw_excerpt=_decode_excerpt(raw),
        )
    except TimeoutError as exc:
        raise HealthCheckHttpTimeoutError("健康检查请求超时") from exc
    except urllib.error.URLError as exc:
        reason = exc.reason
        if isinstance(reason, TimeoutError):
            raise HealthCheckHttpTimeoutError("健康检查请求超时") from exc

        message = str(reason).strip() or "健康检查请求失败"
        raise HealthCheckHttpRequestError(message) from exc
    except (OSError, ValueError) as exc:
        message = str(exc).strip() or "健康检查请求失败"
        raise HealthCheckHttpRequestError(message) from exc


def _latency_ms(started_perf: float) -> int:
    return max(0, int((perf_counter() - started_perf) * 1000))


def _run_out(row: AppRegistryHealthCheckRun) -> AppRegistryHealthCheckRunOut:
    return AppRegistryHealthCheckRunOut(
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


class AppRegistryRuntimeGovernanceService:
    def __init__(
        self,
        db: Session,
        *,
        http_status_probe: HttpStatusProbe = default_http_status_probe,
    ) -> None:
        self.repo = AppRegistryRuntimeGovernanceRepository(db)
        self.http_status_probe = http_status_probe

    def run_health_check_once(self, health_check_id: int) -> AppRegistryHealthCheckRunOut:
        health_check = self.repo.get_health_check(health_check_id)
        if health_check is None:
            raise AppRegistryHealthCheckNotFoundError("健康检查配置不存在")

        endpoint = self.repo.get_endpoint(int(health_check.endpoint_id))
        if endpoint is None:
            raise AppRegistryHealthCheckNotFoundError("健康检查端点不存在")

        self._validate_health_check(health_check, endpoint)

        started_at = datetime.now(UTC)
        started_perf = perf_counter()

        try:
            probe_result = self.http_status_probe(
                str(endpoint.url),
                max(int(health_check.timeout_ms) / 1000, 0.001),
            )
        except HealthCheckHttpTimeoutError as exc:
            row = self._build_run_row(
                health_check=health_check,
                started_at=started_at,
                started_perf=started_perf,
                status="timeout",
                http_status=None,
                message=str(exc),
                raw_excerpt=None,
            )
        except HealthCheckHttpRequestError as exc:
            row = self._build_run_row(
                health_check=health_check,
                started_at=started_at,
                started_perf=started_perf,
                status="error",
                http_status=None,
                message=str(exc),
                raw_excerpt=None,
            )
        else:
            expected_status = int(health_check.expected_status)
            actual_status = int(probe_result.http_status)

            if actual_status == expected_status:
                status = "success"
                message = f"HTTP status matched expected status {expected_status}"
            else:
                status = "failure"
                message = (
                    f"HTTP status {actual_status} did not match expected status "
                    f"{expected_status}"
                )

            row = self._build_run_row(
                health_check=health_check,
                started_at=started_at,
                started_perf=started_perf,
                status=status,
                http_status=actual_status,
                message=message,
                raw_excerpt=probe_result.raw_excerpt,
            )

        saved = self.repo.create_health_check_run(row)
        return _run_out(saved)

    def _validate_health_check(
        self,
        health_check: AppRegistryHealthCheck,
        endpoint: AppRegistryEndpoint,
    ) -> None:
        if not health_check.is_active:
            raise AppRegistryHealthCheckInactiveError("健康检查配置未启用")

        if not endpoint.is_active:
            raise AppRegistryHealthCheckInactiveError("健康检查端点未启用")

        if str(health_check.check_type) != "http_status":
            raise AppRegistryHealthCheckUnsupportedError("当前仅支持 http_status 健康检查")

        method = (endpoint.method or "GET").upper()
        if method != "GET":
            raise AppRegistryHealthCheckUnsupportedError("当前仅支持 GET 健康检查端点")

    def _build_run_row(
        self,
        *,
        health_check: AppRegistryHealthCheck,
        started_at: datetime,
        started_perf: float,
        status: str,
        http_status: int | None,
        message: str,
        raw_excerpt: str | None,
    ) -> AppRegistryHealthCheckRun:
        return AppRegistryHealthCheckRun(
            health_check_id=int(health_check.id),
            started_at=started_at,
            finished_at=datetime.now(UTC),
            status=status,
            http_status=http_status,
            latency_ms=_latency_ms(started_perf),
            message=_limit(message, MAX_MESSAGE_LENGTH),
            raw_excerpt=_limit(raw_excerpt, MAX_RAW_EXCERPT_LENGTH)
            if raw_excerpt is not None
            else None,
        )


__all__ = [
    "AppRegistryHealthCheckInactiveError",
    "AppRegistryHealthCheckNotFoundError",
    "AppRegistryHealthCheckUnsupportedError",
    "AppRegistryRuntimeGovernanceSaveError",
    "AppRegistryRuntimeGovernanceService",
    "HealthCheckHttpRequestError",
    "HealthCheckHttpTimeoutError",
    "HttpStatusProbeResult",
]
