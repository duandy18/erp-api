from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.page_registry.contracts.page_registry_navigation import ErpNavigationOut
from app.page_registry.services.page_registry_navigation_service import (
    PageRegistryNavigationService,
)

router = APIRouter(prefix="/erp/page-registry", tags=["erp-page-registry"])

DBSessionDep = Annotated[Session, Depends(get_db)]


@router.get("/navigation", response_model=ErpNavigationOut)
def get_erp_navigation(db: DBSessionDep) -> ErpNavigationOut:
    return PageRegistryNavigationService(db).list_navigation()


__all__ = ["router"]
