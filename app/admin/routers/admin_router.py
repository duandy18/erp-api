from __future__ import annotations

from fastapi import APIRouter

from app.admin.routers.users_routes import router as users_router

router = APIRouter()
router.include_router(users_router)

__all__ = ["router"]
