from __future__ import annotations

from fastapi import FastAPI

from app.admin.routers.admin_router import router as admin_router
from app.health.router import router as health_router
from app.iam.routers.iam_router import router as iam_router
from app.page_registry.routers.page_registry_routes import router as page_registry_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="ERP Control Plane API",
        version="0.1.0",
        description="ERP control plane API.",
    )
    app.include_router(health_router)
    app.include_router(iam_router)
    app.include_router(page_registry_router)
    app.include_router(admin_router)
    return app


app = create_app()
