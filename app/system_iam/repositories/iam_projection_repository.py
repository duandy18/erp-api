from __future__ import annotations

from collections.abc import Sequence

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


class SystemIamProjectionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_apps(self, app_code: str | None = None) -> list[AppRegistryApp]:
        query = self.db.query(AppRegistryApp).filter(
            AppRegistryApp.is_active.is_(True),
            AppRegistryApp.code != "erp",
        )
        if app_code:
            query = query.filter(AppRegistryApp.code == app_code)
        return query.order_by(AppRegistryApp.sort_order.asc(), AppRegistryApp.code.asc()).all()

    def list_latest_sync_runs(self, app_codes: Sequence[str]) -> list[AppRegistryIamSyncRun]:
        if not app_codes:
            return []

        rows = (
            self.db.query(AppRegistryIamSyncRun)
            .filter(AppRegistryIamSyncRun.app_code.in_(list(app_codes)))
            .order_by(
                AppRegistryIamSyncRun.app_code.asc(),
                AppRegistryIamSyncRun.started_at.desc(),
                AppRegistryIamSyncRun.id.desc(),
            )
            .all()
        )

        latest_by_app: dict[str, AppRegistryIamSyncRun] = {}
        for row in rows:
            latest_by_app.setdefault(str(row.app_code), row)

        return [latest_by_app[app_code] for app_code in app_codes if app_code in latest_by_app]

    def list_users(self, app_codes: Sequence[str]) -> list[AppRegistryIamUserProjection]:
        if not app_codes:
            return []

        return (
            self.db.query(AppRegistryIamUserProjection)
            .filter(AppRegistryIamUserProjection.app_code.in_(list(app_codes)))
            .order_by(
                AppRegistryIamUserProjection.app_code.asc(),
                AppRegistryIamUserProjection.source_user_id.asc(),
            )
            .all()
        )

    def list_permissions(
        self,
        app_codes: Sequence[str],
    ) -> list[AppRegistryIamPermissionProjection]:
        if not app_codes:
            return []

        return (
            self.db.query(AppRegistryIamPermissionProjection)
            .filter(AppRegistryIamPermissionProjection.app_code.in_(list(app_codes)))
            .order_by(
                AppRegistryIamPermissionProjection.app_code.asc(),
                AppRegistryIamPermissionProjection.permission_code.asc(),
            )
            .all()
        )

    def list_user_permissions(
        self,
        app_codes: Sequence[str],
    ) -> list[AppRegistryIamUserPermissionProjection]:
        if not app_codes:
            return []

        return (
            self.db.query(AppRegistryIamUserPermissionProjection)
            .filter(AppRegistryIamUserPermissionProjection.app_code.in_(list(app_codes)))
            .order_by(
                AppRegistryIamUserPermissionProjection.app_code.asc(),
                AppRegistryIamUserPermissionProjection.source_user_id.asc(),
                AppRegistryIamUserPermissionProjection.permission_code.asc(),
            )
            .all()
        )

    def list_pages(self, app_codes: Sequence[str]) -> list[AppRegistryIamPageProjection]:
        if not app_codes:
            return []

        return (
            self.db.query(AppRegistryIamPageProjection)
            .filter(AppRegistryIamPageProjection.app_code.in_(list(app_codes)))
            .order_by(
                AppRegistryIamPageProjection.app_code.asc(),
                AppRegistryIamPageProjection.level.asc(),
                AppRegistryIamPageProjection.sort_order.asc().nullslast(),
                AppRegistryIamPageProjection.page_code.asc(),
            )
            .all()
        )

    def list_route_prefixes(
        self,
        app_codes: Sequence[str],
    ) -> list[AppRegistryIamPageRoutePrefixProjection]:
        if not app_codes:
            return []

        return (
            self.db.query(AppRegistryIamPageRoutePrefixProjection)
            .filter(AppRegistryIamPageRoutePrefixProjection.app_code.in_(list(app_codes)))
            .order_by(
                AppRegistryIamPageRoutePrefixProjection.app_code.asc(),
                AppRegistryIamPageRoutePrefixProjection.page_code.asc(),
                AppRegistryIamPageRoutePrefixProjection.sort_order.asc().nullslast(),
                AppRegistryIamPageRoutePrefixProjection.route_prefix.asc(),
            )
            .all()
        )


__all__ = ["SystemIamProjectionRepository"]
