from __future__ import annotations

from fastapi import FastAPI

from app.admin.routers.admin_router import router as admin_router
from app.app_registry.routers.app_registry_admin_routes import (
    router as app_registry_admin_router,
)
from app.app_registry.routers.app_registry_routes import router as app_registry_router
from app.app_registry.routers.app_registry_runtime_governance_routes import (
    router as app_registry_runtime_governance_router,
)
from app.health.router import router as health_router
from app.iam.routers.iam_router import router as iam_router
from app.page_registry.routers.page_registry_routes import router as page_registry_router
from app.system_iam.routers import router as system_iam_router
from app.system_monitoring.routers.system_monitoring_check_routes import (
    router as system_monitoring_check_router,
)
from app.system_monitoring.routers.system_monitoring_database_routes import (
    router as system_monitoring_database_router,
)
from app.system_monitoring.routers.system_monitoring_endpoint_routes import (
    router as system_monitoring_endpoint_router,
)
from app.system_monitoring.routers.system_monitoring_remaining_routes import (
    router as system_monitoring_remaining_router,
)
from app.system_monitoring.routers.system_monitoring_routes import (
    router as system_monitoring_router,
)
from app.system_service_auth.routers.system_service_auth_routes import (
    router as system_service_auth_router,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="ERP Control Plane API",
        version="0.1.0",
        description="ERP control plane API.",
    )
    app.include_router(health_router)
    app.include_router(iam_router)
    app.include_router(page_registry_router)
    app.include_router(app_registry_router)
    app.include_router(app_registry_admin_router)
    app.include_router(app_registry_runtime_governance_router)
    app.include_router(system_service_auth_router)
    app.include_router(system_monitoring_router)
    app.include_router(system_monitoring_endpoint_router)
    app.include_router(system_monitoring_database_router)
    app.include_router(system_monitoring_remaining_router)
    app.include_router(system_monitoring_check_router)
    app.include_router(system_iam_router)
    app.include_router(admin_router)
    return app


app = create_app()
