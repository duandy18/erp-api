from __future__ import annotations

from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp


class AppRegistryAdminRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_apps(self) -> list[AppRegistryApp]:
        return (
            self.db.query(AppRegistryApp)
            .order_by(AppRegistryApp.sort_order.asc(), AppRegistryApp.code.asc())
            .all()
        )

    def get_app(self, code: str) -> AppRegistryApp | None:
        return (
            self.db.query(AppRegistryApp)
            .filter(AppRegistryApp.code == code)
            .one_or_none()
        )

    def add_app(self, row: AppRegistryApp) -> None:
        self.db.add(row)


__all__ = ["AppRegistryAdminRepository"]
