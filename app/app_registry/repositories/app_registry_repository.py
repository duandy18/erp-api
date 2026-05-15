from __future__ import annotations

from sqlalchemy.orm import Session

from app.app_registry.models.app_registry_app import AppRegistryApp


class AppRegistryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active_apps(self) -> list[AppRegistryApp]:
        return (
            self.db.query(AppRegistryApp)
            .filter(AppRegistryApp.is_active.is_(True))
            .order_by(AppRegistryApp.sort_order.asc(), AppRegistryApp.code.asc())
            .all()
        )


__all__ = ["AppRegistryRepository"]
