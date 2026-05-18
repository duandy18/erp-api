from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp
from app.app_registry.models.app_registry_iam_projection import (
    AppRegistryIamPageProjection,
    AppRegistryIamPageRoutePrefixProjection,
    AppRegistryIamPermissionProjection,
    AppRegistryIamSyncRun,
    AppRegistryIamUserPermissionProjection,
    AppRegistryIamUserProjection,
)
from app.system_iam.contracts import SystemIamSyncRunOut
from app.system_iam.repositories import (
    SystemIamSnapshotSyncRepository,
    SystemIamSnapshotSyncSaveError,
)

HTTP_TIMEOUT_SECONDS = 5.0
MAX_RAW_EXCERPT_LENGTH = 2048
ERP_SERVICE_CLIENT = "erp-service"
IAM_SNAPSHOT_PATH = "/system/read/v1/iam-snapshot"


class SystemIamSnapshotAppNotFoundError(ValueError):
    pass


class SystemIamSnapshotFetchError(RuntimeError):
    pass


class SystemIamSnapshotPayloadError(ValueError):
    pass


JsonFetcher = Callable[[str, float, Mapping[str, str]], dict[str, Any]]


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


def default_iam_snapshot_fetcher(
    url: str,
    timeout_seconds: float,
    headers: Mapping[str, str],
) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent": "erp-control-plane-iam-snapshot-sync/0.1",
            **dict(headers),
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read()
            text = raw.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raw_excerpt = _decode_excerpt(exc.read(MAX_RAW_EXCERPT_LENGTH * 4))
        message = f"读取 IAM 快照失败: HTTP {int(exc.code)} {url}"
        if raw_excerpt:
            message = f"{message}: {raw_excerpt}"
        raise SystemIamSnapshotFetchError(message) from exc
    except TimeoutError as exc:
        raise SystemIamSnapshotFetchError(f"读取 IAM 快照超时: {url}") from exc
    except urllib.error.URLError as exc:
        raise SystemIamSnapshotFetchError(
            f"读取 IAM 快照失败: {str(exc.reason)}"
        ) from exc
    except OSError as exc:
        raise SystemIamSnapshotFetchError(f"读取 IAM 快照失败: {exc}") from exc

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemIamSnapshotPayloadError(f"IAM 快照接口返回非 JSON: {url}") from exc

    if not isinstance(payload, dict):
        raise SystemIamSnapshotPayloadError(f"IAM 快照接口返回结构不是对象: {url}")

    return payload


def _run_out(row: AppRegistryIamSyncRun) -> SystemIamSyncRunOut:
    return SystemIamSyncRunOut(
        id=int(row.id),
        app_code=str(row.app_code),
        source_base_url=str(row.source_base_url),
        status=str(row.status),
        started_at=row.started_at,
        finished_at=row.finished_at,
        source_snapshot_at=row.source_snapshot_at,
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
        raise SystemIamSnapshotPayloadError(f"{field_name} 必须是非空字符串")
    return value.strip()


def _optional_str(payload: Mapping[str, Any], field_name: str) -> str | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise SystemIamSnapshotPayloadError(f"{field_name} 必须是字符串")
    text = value.strip()
    return text or None


def _required_bool(payload: Mapping[str, Any], field_name: str) -> bool:
    value = payload.get(field_name)
    if not isinstance(value, bool):
        raise SystemIamSnapshotPayloadError(f"{field_name} 必须是布尔值")
    return value


def _optional_bool(payload: Mapping[str, Any], field_name: str) -> bool | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise SystemIamSnapshotPayloadError(f"{field_name} 必须是布尔值或 null")
    return value


def _required_int(payload: Mapping[str, Any], field_name: str) -> int:
    value = payload.get(field_name)
    if isinstance(value, bool) or not isinstance(value, int):
        raise SystemIamSnapshotPayloadError(f"{field_name} 必须是整数")
    return value


def _optional_int(payload: Mapping[str, Any], field_name: str) -> int | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise SystemIamSnapshotPayloadError(f"{field_name} 必须是整数或 null")
    return value


def _optional_datetime(payload: Mapping[str, Any], field_name: str) -> datetime | None:
    value = payload.get(field_name)
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if not isinstance(value, str) or not value.strip():
        raise SystemIamSnapshotPayloadError(f"{field_name} 必须是 ISO 时间字符串或 null")

    text = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError as exc:
        raise SystemIamSnapshotPayloadError(
            f"{field_name} 必须是 ISO 时间字符串或 null"
        ) from exc


def _list_payload(payload: Mapping[str, Any], field_name: str) -> list[dict[str, Any]]:
    value = payload.get(field_name)
    if not isinstance(value, list):
        raise SystemIamSnapshotPayloadError(f"{field_name} 必须是列表")

    rows: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise SystemIamSnapshotPayloadError(f"{field_name} 内元素必须是对象")
        rows.append(dict(item))

    return rows


class SystemIamSnapshotSyncService:
    def __init__(
        self,
        db: Session,
        *,
        repository: SystemIamSnapshotSyncRepository | None = None,
        json_fetcher: JsonFetcher = default_iam_snapshot_fetcher,
    ) -> None:
        self.repo = repository or SystemIamSnapshotSyncRepository(db)
        self.json_fetcher = json_fetcher

    def sync_iam_snapshot(self, code: str) -> SystemIamSyncRunOut:
        app_code = code.strip()
        app_row = self.repo.get_app(app_code)
        if app_row is None:
            raise SystemIamSnapshotAppNotFoundError("应用不存在")

        source_base_url = str(app_row.local_api_url).rstrip("/")
        run = AppRegistryIamSyncRun(
            app_code=app_code,
            source_base_url=source_base_url,
            status="running",
            started_at=datetime.now(UTC),
        )
        self.repo.add(run)
        self.repo.flush()

        try:
            payload = self._fetch_snapshot(source_base_url)
            self._assert_snapshot_app(payload, app_row)
        except (SystemIamSnapshotFetchError, SystemIamSnapshotPayloadError) as exc:
            self._mark_run_failure(run, exc)
            raise

        now = datetime.now(UTC)
        stats = SyncStats()

        try:
            run.source_snapshot_at = _optional_datetime(payload, "snapshot_at")
            stats.add(self._sync_users(app_code, payload, run, now))
            stats.add(self._sync_permissions(app_code, payload, run, now))
            stats.add(self._sync_user_permissions(app_code, payload, run, now))
            stats.add(self._sync_pages(app_code, payload, run, now))
            stats.add(self._sync_route_prefixes(app_code, payload, run, now))

            run.status = "success"
            run.finished_at = now
            run.fetched_count = stats.fetched
            run.inserted_count = stats.inserted
            run.updated_count = stats.updated
            run.deleted_count = stats.deleted

            self.repo.commit()
            self.repo.refresh(run)
        except SystemIamSnapshotSyncSaveError:
            raise
        except Exception as exc:
            self.repo.rollback()
            raise SystemIamSnapshotSyncSaveError("IAM 快照同步投影保存失败") from exc

        return _run_out(run)

    def _fetch_snapshot(self, source_base_url: str) -> dict[str, Any]:
        return self.json_fetcher(
            _join_url(source_base_url, IAM_SNAPSHOT_PATH),
            HTTP_TIMEOUT_SECONDS,
            {"X-Service-Client": ERP_SERVICE_CLIENT},
        )

    def _mark_run_failure(
        self,
        run: AppRegistryIamSyncRun,
        exc: Exception,
    ) -> None:
        run.status = "failure"
        run.finished_at = datetime.now(UTC)
        run.error_message = _limit(str(exc))
        run.raw_excerpt = None
        self.repo.commit()
        self.repo.refresh(run)

    @staticmethod
    def _assert_snapshot_app(
        payload: Mapping[str, Any],
        app_row: AppRegistryApp,
    ) -> None:
        payload_app_code = _required_str(payload, "app_code")
        if payload_app_code != str(app_row.code):
            raise SystemIamSnapshotPayloadError("IAM 快照 app_code 与目标应用不一致")

    def _sync_users(
        self,
        app_code: str,
        payload: Mapping[str, Any],
        run: AppRegistryIamSyncRun,
        synced_at: datetime,
    ) -> SyncStats:
        users = _list_payload(payload, "users")
        existing = {
            int(row.source_user_id): row
            for row in self.repo.list_users(app_code)
        }
        seen: set[int] = set()
        stats = SyncStats(fetched=len(users))

        for user in users:
            source_user_id = _required_int(user, "user_id")
            row = existing.get(source_user_id)

            if row is None:
                row = AppRegistryIamUserProjection(
                    app_code=app_code,
                    source_user_id=source_user_id,
                )
                self.repo.add(row)
                stats.inserted += 1
            else:
                stats.updated += 1

            seen.add(source_user_id)
            row.username = _required_str(user, "username")
            row.is_active = _required_bool(user, "is_active")
            row.full_name = _optional_str(user, "full_name")
            row.phone = _optional_str(user, "phone")
            row.email = _optional_str(user, "email")
            row.raw_payload = user
            row.last_sync_run_id = int(run.id)
            row.last_synced_at = synced_at

        for source_user_id, row in existing.items():
            if source_user_id not in seen:
                self.repo.delete(row)
                stats.deleted += 1

        return stats

    def _sync_permissions(
        self,
        app_code: str,
        payload: Mapping[str, Any],
        run: AppRegistryIamSyncRun,
        synced_at: datetime,
    ) -> SyncStats:
        permissions = _list_payload(payload, "permissions")
        existing = {
            str(row.permission_code): row
            for row in self.repo.list_permissions(app_code)
        }
        seen: set[str] = set()
        stats = SyncStats(fetched=len(permissions))

        for permission in permissions:
            permission_code = _required_str(permission, "permission_code")
            row = existing.get(permission_code)

            if row is None:
                row = AppRegistryIamPermissionProjection(
                    app_code=app_code,
                    permission_code=permission_code,
                )
                self.repo.add(row)
                stats.inserted += 1
            else:
                stats.updated += 1

            seen.add(permission_code)
            row.source_permission_id = _required_int(permission, "permission_id")
            row.raw_payload = permission
            row.last_sync_run_id = int(run.id)
            row.last_synced_at = synced_at

        for permission_code, row in existing.items():
            if permission_code not in seen:
                self.repo.delete(row)
                stats.deleted += 1

        return stats

    def _sync_user_permissions(
        self,
        app_code: str,
        payload: Mapping[str, Any],
        run: AppRegistryIamSyncRun,
        synced_at: datetime,
    ) -> SyncStats:
        user_permissions = _list_payload(payload, "user_permissions")
        existing = {
            (int(row.source_user_id), str(row.permission_code)): row
            for row in self.repo.list_user_permissions(app_code)
        }
        seen: set[tuple[int, str]] = set()
        stats = SyncStats(fetched=len(user_permissions))

        for user_permission in user_permissions:
            source_user_id = _required_int(user_permission, "user_id")
            permission_code = _required_str(user_permission, "permission_code")
            key = (source_user_id, permission_code)
            row = existing.get(key)

            if row is None:
                row = AppRegistryIamUserPermissionProjection(
                    app_code=app_code,
                    source_user_id=source_user_id,
                    permission_code=permission_code,
                )
                self.repo.add(row)
                stats.inserted += 1
            else:
                stats.updated += 1

            seen.add(key)
            row.source_permission_id = _required_int(user_permission, "permission_id")
            row.granted_at = _optional_datetime(user_permission, "granted_at")
            row.raw_payload = user_permission
            row.last_sync_run_id = int(run.id)
            row.last_synced_at = synced_at

        for key, row in existing.items():
            if key not in seen:
                self.repo.delete(row)
                stats.deleted += 1

        return stats

    def _sync_pages(
        self,
        app_code: str,
        payload: Mapping[str, Any],
        run: AppRegistryIamSyncRun,
        synced_at: datetime,
    ) -> SyncStats:
        pages = _list_payload(payload, "page_registry")
        existing = {
            str(row.page_code): row
            for row in self.repo.list_pages(app_code)
        }
        seen: set[str] = set()
        stats = SyncStats(fetched=len(pages))

        for page in pages:
            page_code = _required_str(page, "page_code")
            row = existing.get(page_code)

            if row is None:
                row = AppRegistryIamPageProjection(
                    app_code=app_code,
                    page_code=page_code,
                )
                self.repo.add(row)
                stats.inserted += 1
            else:
                stats.updated += 1

            seen.add(page_code)
            row.page_name = _required_str(page, "page_name")
            row.parent_page_code = _optional_str(page, "parent_page_code")
            row.level = _required_int(page, "level")
            row.domain_code = _optional_str(page, "domain_code")
            row.show_in_topbar = _required_bool(page, "show_in_topbar")
            row.show_in_sidebar = _required_bool(page, "show_in_sidebar")
            row.inherit_permissions = _required_bool(page, "inherit_permissions")
            row.read_permission_code = _optional_str(page, "read_permission_code")
            row.write_permission_code = _optional_str(page, "write_permission_code")
            row.sort_order = _optional_int(page, "sort_order")
            row.is_active = _optional_bool(page, "is_active")
            row.raw_payload = page
            row.last_sync_run_id = int(run.id)
            row.last_synced_at = synced_at

        for page_code, row in existing.items():
            if page_code not in seen:
                self.repo.delete(row)
                stats.deleted += 1

        return stats

    def _sync_route_prefixes(
        self,
        app_code: str,
        payload: Mapping[str, Any],
        run: AppRegistryIamSyncRun,
        synced_at: datetime,
    ) -> SyncStats:
        route_prefixes = _list_payload(payload, "page_route_prefixes")
        existing = {
            (str(row.page_code), str(row.route_prefix)): row
            for row in self.repo.list_route_prefixes(app_code)
        }
        seen: set[tuple[str, str]] = set()
        stats = SyncStats(fetched=len(route_prefixes))

        for route_prefix in route_prefixes:
            page_code = _required_str(route_prefix, "page_code")
            path = _required_str(route_prefix, "route_prefix")
            key = (page_code, path)
            row = existing.get(key)

            if row is None:
                row = AppRegistryIamPageRoutePrefixProjection(
                    app_code=app_code,
                    page_code=page_code,
                    route_prefix=path,
                )
                self.repo.add(row)
                stats.inserted += 1
            else:
                stats.updated += 1

            seen.add(key)
            row.sort_order = _optional_int(route_prefix, "sort_order")
            row.is_active = _optional_bool(route_prefix, "is_active")
            row.raw_payload = route_prefix
            row.last_sync_run_id = int(run.id)
            row.last_synced_at = synced_at

        for key, row in existing.items():
            if key not in seen:
                self.repo.delete(row)
                stats.deleted += 1

        return stats


__all__ = [
    "ERP_SERVICE_CLIENT",
    "IAM_SNAPSHOT_PATH",
    "JsonFetcher",
    "SystemIamSnapshotAppNotFoundError",
    "SystemIamSnapshotFetchError",
    "SystemIamSnapshotPayloadError",
    "SystemIamSnapshotSyncSaveError",
    "SystemIamSnapshotSyncService",
    "default_iam_snapshot_fetcher",
]
