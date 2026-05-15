from __future__ import annotations

from fastapi import FastAPI

from app.health.router import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="ERP Control Plane API",
        version="0.1.0",
        description="ERP control plane API.",
    )
    app.include_router(health_router)
    return app


app = create_app()
