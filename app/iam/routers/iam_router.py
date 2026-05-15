from __future__ import annotations

from fastapi import APIRouter

from app.iam.routers.auth_routes import router as auth_router
from app.iam.routers.me_routes import router as me_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(me_router)

__all__ = ["router"]
