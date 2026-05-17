from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.app_registry.contracts.app_registry_self_description_sync_contracts import (
    AppRegistrySelfDescriptionSyncRunOut,
)
from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_self_description_projection import (
    AppRegistryAppManifestSnapshot,
    AppRegistryPageCatalogPage,
    AppRegistrySelfDescriptionSyncRun,
    AppRegistryServiceCapabilityCatalog,
    AppRegistryServiceCapabilityRoute,
    AppRegistryServiceDependencyCatalog,
    AppRegistryServiceDependencyEndpoint,
)
from app.app_registry.repositories.app_registry_self_description_sync_repository import (
    AppRegistrySelfDescriptionSyncRepository,
    AppRegistrySelfDescriptionSyncSaveError,
)

HTTP_TIMEOUT_SECONDS = 5.0
MAX_RAW_EXCERPT_LENGTH = 2048


class AppRegistrySelfDescriptionAppNotFoundError(ValueError):
    pass


class AppRegistrySelfDescriptionFetchError(RuntimeError):
    pass


class AppRegistrySelfDescriptionPayloadError(ValueError):
    pass


JsonFetcher = Callable[[str, float], dict[str, Any]]


@dataclass
class SyncStats:
    fetched: int = 0
    inserted: int = 0
    updated: int = 0
    deleted: int = 0

    def add(self, other: SyncStats) -> None:
        self.fetched += other.fetched
        self.inserted += other.inserted
        self.updated += other.updated
        self.deleted += other.deleted


def _limit(value: str, max_length: int = MAX_RAW_EXCERPT_LENGTH) -> str:
    if len(value) <= max_length:
        return value
    return value[:max_length]


def _decode_excerpt(raw: bytes) -> str | None:
    if not raw:
        return None

    text = raw.decode("utf-8", errors="replace").strip()
    if not text:
        return None

    return _limit(text)


def default_json_fetcher(url: str, timeout_seconds: float) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "erp-control-plane-self-description-sync/0.1"},
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read(MAX_RAW_EXCERPT_LENGTH * 8)
            text = raw.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raise AppRegistrySelfDescriptionFetchError(
            f"读取自描述接口失败: HTTP {int(exc.code)} {url}"
        ) from exc
    except TimeoutError as exc:
        raise AppRegistrySelfDescriptionFetchError(f"读取自描述接口超时: {url}") from exc
    except urllib.error.URLError as exc:
        raise AppRegistrySelfDescriptionFetchError(
            f"读取自描述接口失败: {str(exc.reason)}"
        ) from exc
    except OSError as exc:
        raise AppRegistrySelfDescriptionFetchError(f"读取自描述接口失败: {exc}") from exc

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AppRegistrySelfDescriptionPayloadError(
            f"自描述接口返回非 JSON: {url}"
        ) from exc

    if not isinstance(payload, dict):
        raise AppRegistrySelfDescriptionPayloadError(f"自描述接口返回结构不是对象: {url}")

    return payload


def _run_out(row: AppRegistrySelfDescriptionSyncRun) -> AppRegistrySelfDescriptionSyncRunOut:
    return AppRegistrySelfDescriptionSyncRunOut(
        id=int(row.id),
        app_code=str(row.app_code),
        sync_type=str(row.sync_type),
        source_base_url=str(row.source_base_url),
        status=str(row.status),
        started_at=row.started_at,
        finished_at=row.finished_at,
        fetched_count=int(row.fetched_count),
        inserted_count=int(row.inserted_count),
        updated_count=int(row.updated_count),
        deleted_count=int(row.deleted_count),
        error_message=row.error_message,
        raw_excerpt=row.raw_excerpt,
    )


def _join_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


def _required_str(payload: Mapping[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise AppRegistrySelfDescriptionPayloadError(f"{field_name} 必须是非空字符串")
    return value.strip()


def _optional_str(payload: Mapping[str, Any], field_name: str) -> str | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise AppRegistrySelfDescriptionPayloadError(f"{field_name} 必须是字符串")
    text = value.strip()
    return text or None


def _required_bool(payload: Mapping[str, Any], field_name: str) -> bool:
    value = payload.get(field_name)
    if not isinstance(value, bool):
        raise AppRegistrySelfDescriptionPayloadError(f"{field_name} 必须是布尔值")
    return value


def _required_int(payload: Mapping[str, Any], field_name: str) -> int:
    value = payload.get(field_name)
    if isinstance(value, bool) or not isinstance(value, int):
        raise AppRegistrySelfDescriptionPayloadError(f"{field_name} 必须是整数")
    return value


def _optional_datetime(payload: Mapping[str, Any], field_name: str) -> datetime | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str) or not value.strip():
        raise AppRegistrySelfDescriptionPayloadError(f"{field_name} 必须是时间字符串")

    text = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError as exc:
        raise AppRegistrySelfDescriptionPayloadError(
            f"{field_name} 必须是 ISO 时间字符串"
        ) from exc


def _list_payload(payload: Mapping[str, Any], field_name: str) -> list[dict[str, Any]]:
    value = payload.get(field_name)
    if not isinstance(value, list):
        raise AppRegistrySelfDescriptionPayloadError(f"{field_name} 必须是列表")

    rows: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise AppRegistrySelfDescriptionPayloadError(f"{field_name} 内元素必须是对象")
        rows.append(dict(item))

    return rows


def _string_list(payload: Mapping[str, Any], field_name: str) -> list[str]:
    value = payload.get(field_name)
    if value is None:
        return []
    if not isinstance(value, list):
        raise AppRegistrySelfDescriptionPayloadError(f"{field_name} 必须是字符串列表")

    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise AppRegistrySelfDescriptionPayloadError(f"{field_name} 内元素必须是字符串")
        text = item.strip()
        if text:
            result.append(text)
    return result


class AppRegistrySelfDescriptionSyncService:
    def __init__(
        self,
        db: Session,
        *,
        json_fetcher: JsonFetcher = default_json_fetcher,
        repository: AppRegistrySelfDescriptionSyncRepository | None = None,
    ) -> None:
        self.repo = repository or AppRegistrySelfDescriptionSyncRepository(db)
        self.json_fetcher = json_fetcher

    def sync_app_self_description(self, code: str) -> AppRegistrySelfDescriptionSyncRunOut:
        app_code = code.strip()
        app_row = self.repo.get_app(app_code)
        if app_row is None:
            raise AppRegistrySelfDescriptionAppNotFoundError("应用不存在")

        source_base_url = str(app_row.local_api_url).rstrip("/")
        run = AppRegistrySelfDescriptionSyncRun(
            app_code=app_code,
            sync_type="all",
            source_base_url=source_base_url,
            status="running",
            started_at=datetime.now(UTC),
        )
        self.repo.add(run)
        self.repo.flush()

        try:
            payloads = self._fetch_all(source_base_url)
        except (
            AppRegistrySelfDescriptionFetchError,
            AppRegistrySelfDescriptionPayloadError,
        ) as exc:
            self._mark_run_failure(run, exc)
            raise

        stats = SyncStats()
        now = datetime.now(UTC)

        try:
            stats.add(self._sync_manifest(app_row, payloads["manifest"], run, now))
            stats.add(self._sync_page_catalog(app_code, payloads["page_catalog"], run, now))
            stats.add(
                self._sync_service_capabilities(
                    app_code,
                    payloads["service_capabilities"],
                    run,
                    now,
                )
            )
            stats.add(
                self._sync_service_dependencies(
                    app_code,
                    payloads["service_dependencies"],
                    run,
                    now,
                )
            )

            run.status = "success"
            run.finished_at = now
            run.fetched_count = stats.fetched
            run.inserted_count = stats.inserted
            run.updated_count = stats.updated
            run.deleted_count = stats.deleted

            self.repo.commit()
            self.repo.refresh(run)
        except AppRegistrySelfDescriptionSyncSaveError:
            raise
        except Exception as exc:
            self.repo.rollback()
            raise AppRegistrySelfDescriptionSyncSaveError(
                "自描述同步投影保存失败"
            ) from exc

        return _run_out(run)

    def _fetch_all(self, source_base_url: str) -> dict[str, dict[str, Any]]:
        return {
            "manifest": self.json_fetcher(
                _join_url(source_base_url, "/system/read/v1/app-manifest"),
                HTTP_TIMEOUT_SECONDS,
            ),
            "page_catalog": self.json_fetcher(
                _join_url(source_base_url, "/system/read/v1/page-catalog"),
                HTTP_TIMEOUT_SECONDS,
            ),
            "service_capabilities": self.json_fetcher(
                _join_url(source_base_url, "/system/read/v1/service-capabilities"),
                HTTP_TIMEOUT_SECONDS,
            ),
            "service_dependencies": self.json_fetcher(
                _join_url(source_base_url, "/system/read/v1/service-dependencies"),
                HTTP_TIMEOUT_SECONDS,
            ),
        }

    def _mark_run_failure(
        self,
        run: AppRegistrySelfDescriptionSyncRun,
        exc: Exception,
    ) -> None:
        run.status = "failure"
        run.finished_at = datetime.now(UTC)
        run.error_message = _limit(str(exc), 2048)
        run.raw_excerpt = None
        self.repo.commit()
        self.repo.refresh(run)

    def _sync_manifest(
        self,
        app_row: AppRegistryApp,
        payload: dict[str, Any],
        run: AppRegistrySelfDescriptionSyncRun,
        synced_at: datetime,
    ) -> SyncStats:
        app_code = _required_str(payload, "app_code")
        if app_code != app_row.code:
            raise AppRegistrySelfDescriptionPayloadError("manifest app_code 与目标应用不一致")

        row = self.repo.get_manifest_snapshot(app_code)
        stats = SyncStats(fetched=1)

        if row is None:
            row = AppRegistryAppManifestSnapshot(app_code=app_code)
            self.repo.add(row)
            stats.inserted += 1
        else:
            stats.updated += 1

        build_info = payload.get("build_info")
        if not isinstance(build_info, dict):
            build_info = {}

        row.app_name = _required_str(payload, "app_name")
        row.app_type = _required_str(payload, "app_type")
        row.status = _required_str(payload, "status")
        row.description = _required_str(payload, "description")
        row.default_web_path = _required_str(payload, "default_web_path")
        row.default_api_path = _required_str(payload, "default_api_path")
        row.local_web_url = _required_str(payload, "local_web_url")
        row.local_api_url = _required_str(payload, "local_api_url")
        row.health_url = _required_str(payload, "health_url")
        row.db_health_url = _optional_str(payload, "db_health_url")
        row.openapi_url = _required_str(payload, "openapi_url")
        row.page_catalog_url = _required_str(payload, "page_catalog_url")
        row.service_capabilities_url = _required_str(
            payload,
            "service_capabilities_url",
        )
        row.service_dependencies_url = _required_str(
            payload,
            "service_dependencies_url",
        )
        row.version = _required_str(payload, "version")
        row.build_environment = _optional_str(build_info, "environment")
        row.build_git_sha = _optional_str(build_info, "git_sha")
        row.build_time = _optional_str(build_info, "build_time")
        row.raw_manifest = payload
        row.last_sync_run_id = int(run.id)
        row.last_synced_at = synced_at

        return stats

    def _sync_page_catalog(
        self,
        app_code: str,
        payload: dict[str, Any],
        run: AppRegistrySelfDescriptionSyncRun,
        synced_at: datetime,
    ) -> SyncStats:
        self._assert_catalog_app(payload, app_code)
        pages = _list_payload(payload, "pages")
        existing = {
            str(row.page_code): row
            for row in self.repo.list_page_catalog_pages(app_code)
        }
        seen: set[str] = set()
        stats = SyncStats(fetched=len(pages))

        for page in pages:
            page_code = _required_str(page, "page_code")
            row = existing.get(page_code)

            if row is None:
                row = AppRegistryPageCatalogPage(app_code=app_code, page_code=page_code)
                self.repo.add(row)
                stats.inserted += 1
            else:
                stats.updated += 1

            seen.add(page_code)
            row.page_name = _required_str(page, "page_name")
            row.route_path = _optional_str(page, "route_path")
            row.parent_page_code = _optional_str(page, "parent_page_code")
            row.level = _required_int(page, "level")
            row.read_permission_code = _optional_str(page, "read_permission_code")
            row.write_permission_code = _optional_str(page, "write_permission_code")
            row.is_active = _required_bool(page, "is_active")
            row.sort_order = _required_int(page, "sort_order")
            row.source_updated_at = _optional_datetime(page, "source_updated_at")
            row.raw_payload = page
            row.last_sync_run_id = int(run.id)
            row.last_synced_at = synced_at

        for page_code, row in existing.items():
            if page_code not in seen:
                self.repo.delete(row)
                stats.deleted += 1

        return stats

    def _sync_service_capabilities(
        self,
        app_code: str,
        payload: dict[str, Any],
        run: AppRegistrySelfDescriptionSyncRun,
        synced_at: datetime,
    ) -> SyncStats:
        self._assert_catalog_app(payload, app_code)
        capabilities = _list_payload(payload, "capabilities")
        stats = self._sync_capability_catalog(app_code, capabilities, run, synced_at)
        stats.add(self._sync_capability_routes(app_code, capabilities, run, synced_at))
        return stats

    def _sync_capability_catalog(
        self,
        app_code: str,
        capabilities: list[dict[str, Any]],
        run: AppRegistrySelfDescriptionSyncRun,
        synced_at: datetime,
    ) -> SyncStats:
        existing = {
            str(row.capability_code): row
            for row in self.repo.list_service_capabilities(app_code)
        }
        seen: set[str] = set()
        stats = SyncStats(fetched=len(capabilities))

        for capability in capabilities:
            capability_code = _required_str(capability, "capability_code")
            row = existing.get(capability_code)

            if row is None:
                row = AppRegistryServiceCapabilityCatalog(
                    app_code=app_code,
                    capability_code=capability_code,
                )
                self.repo.add(row)
                stats.inserted += 1
            else:
                stats.updated += 1

            seen.add(capability_code)
            row.capability_name = _required_str(capability, "capability_name")
            row.resource_code = _required_str(capability, "resource_code")
            row.permission_code = _required_str(capability, "permission_code")
            row.description = _optional_str(capability, "description")
            row.is_active = _required_bool(capability, "is_active")
            row.source_updated_at = _optional_datetime(capability, "source_updated_at")
            row.raw_payload = capability
            row.last_sync_run_id = int(run.id)
            row.last_synced_at = synced_at

        for capability_code, row in existing.items():
            if capability_code not in seen:
                self.repo.delete(row)
                stats.deleted += 1

        return stats

    def _sync_capability_routes(
        self,
        app_code: str,
        capabilities: list[dict[str, Any]],
        run: AppRegistrySelfDescriptionSyncRun,
        synced_at: datetime,
    ) -> SyncStats:
        existing = {
            (
                str(row.capability_code),
                str(row.http_method),
                str(row.path),
            ): row
            for row in self.repo.list_service_capability_routes(app_code)
        }
        seen: set[tuple[str, str, str]] = set()
        stats = SyncStats()

        for capability in capabilities:
            capability_code = _required_str(capability, "capability_code")
            routes = _list_payload(capability, "routes")
            stats.fetched += len(routes)

            for route in routes:
                http_method = _required_str(route, "http_method").upper()
                path = _required_str(route, "path")
                key = (capability_code, http_method, path)
                row = existing.get(key)

                if row is None:
                    row = AppRegistryServiceCapabilityRoute(
                        app_code=app_code,
                        capability_code=capability_code,
                        http_method=http_method,
                        path=path,
                    )
                    self.repo.add(row)
                    stats.inserted += 1
                else:
                    stats.updated += 1

                seen.add(key)
                row.route_name = _required_str(route, "route_name")
                row.auth_required = _required_bool(route, "auth_required")
                row.is_active = _required_bool(route, "is_active")
                row.source_created_at = _optional_datetime(route, "source_created_at")
                row.raw_payload = route
                row.last_sync_run_id = int(run.id)
                row.last_synced_at = synced_at

        for key, row in existing.items():
            if key not in seen:
                self.repo.delete(row)
                stats.deleted += 1

        return stats

    def _sync_service_dependencies(
        self,
        app_code: str,
        payload: dict[str, Any],
        run: AppRegistrySelfDescriptionSyncRun,
        synced_at: datetime,
    ) -> SyncStats:
        self._assert_catalog_app(payload, app_code)
        dependencies = _list_payload(payload, "dependencies")
        stats = self._sync_dependency_catalog(app_code, dependencies, run, synced_at)
        stats.add(self._sync_dependency_endpoints(app_code, dependencies, run, synced_at))
        return stats

    def _sync_dependency_catalog(
        self,
        app_code: str,
        dependencies: list[dict[str, Any]],
        run: AppRegistrySelfDescriptionSyncRun,
        synced_at: datetime,
    ) -> SyncStats:
        existing = {
            str(row.dependency_code): row
            for row in self.repo.list_service_dependencies(app_code)
        }
        seen: set[str] = set()
        stats = SyncStats(fetched=len(dependencies))

        for dependency in dependencies:
            dependency_code = _required_str(dependency, "dependency_code")
            row = existing.get(dependency_code)

            if row is None:
                row = AppRegistryServiceDependencyCatalog(
                    source_app_code=app_code,
                    dependency_code=dependency_code,
                )
                self.repo.add(row)
                stats.inserted += 1
            else:
                stats.updated += 1

            seen.add(dependency_code)
            row.dependency_name = _required_str(dependency, "dependency_name")
            row.target_app_code = _required_str(dependency, "target_app_code")
            row.target_capability_code = _required_str(
                dependency,
                "target_capability_code",
            )
            row.required_permission_code = _required_str(
                dependency,
                "required_permission_code",
            )
            row.description = _optional_str(dependency, "description")
            row.is_required = _required_bool(dependency, "is_required")
            row.is_active = _required_bool(dependency, "is_active")
            row.required_config_keys = _string_list(dependency, "required_config_keys")
            row.source_modules = _string_list(dependency, "source_modules")
            row.raw_payload = dependency
            row.last_sync_run_id = int(run.id)
            row.last_synced_at = synced_at

        for dependency_code, row in existing.items():
            if dependency_code not in seen:
                self.repo.delete(row)
                stats.deleted += 1

        return stats

    def _sync_dependency_endpoints(
        self,
        app_code: str,
        dependencies: list[dict[str, Any]],
        run: AppRegistrySelfDescriptionSyncRun,
        synced_at: datetime,
    ) -> SyncStats:
        existing = {
            (
                str(row.dependency_code),
                str(row.http_method),
                str(row.path),
            ): row
            for row in self.repo.list_service_dependency_endpoints(app_code)
        }
        seen: set[tuple[str, str, str]] = set()
        stats = SyncStats()

        for dependency in dependencies:
            dependency_code = _required_str(dependency, "dependency_code")
            endpoints = _list_payload(dependency, "endpoints")
            stats.fetched += len(endpoints)

            for endpoint in endpoints:
                http_method = _required_str(endpoint, "http_method").upper()
                path = _required_str(endpoint, "path")
                key = (dependency_code, http_method, path)
                row = existing.get(key)

                if row is None:
                    row = AppRegistryServiceDependencyEndpoint(
                        source_app_code=app_code,
                        dependency_code=dependency_code,
                        http_method=http_method,
                        path=path,
                    )
                    self.repo.add(row)
                    stats.inserted += 1
                else:
                    stats.updated += 1

                seen.add(key)
                row.purpose = _optional_str(endpoint, "purpose")
                row.raw_payload = endpoint
                row.last_sync_run_id = int(run.id)
                row.last_synced_at = synced_at

        for key, row in existing.items():
            if key not in seen:
                self.repo.delete(row)
                stats.deleted += 1

        return stats

    @staticmethod
    def _assert_catalog_app(payload: Mapping[str, Any], app_code: str) -> None:
        payload_app_code = _required_str(payload, "app_code")
        if payload_app_code != app_code:
            raise AppRegistrySelfDescriptionPayloadError("payload app_code 与目标应用不一致")


__all__ = [
    "AppRegistrySelfDescriptionAppNotFoundError",
    "AppRegistrySelfDescriptionFetchError",
    "AppRegistrySelfDescriptionPayloadError",
    "AppRegistrySelfDescriptionSyncRunOut",
    "AppRegistrySelfDescriptionSyncSaveError",
    "AppRegistrySelfDescriptionSyncService",
    "JsonFetcher",
    "default_json_fetcher",
]
