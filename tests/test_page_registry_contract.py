from __future__ import annotations

from app.page_registry.contracts.page_registry_navigation import ErpNavigationOut
from app.page_registry.models.page_registry import PageRegistry, PageRoutePrefix, Permission


def test_page_registry_model_shape() -> None:
    assert Permission.__table__.name == "permissions"
    assert PageRegistry.__table__.name == "page_registry"
    assert PageRoutePrefix.__table__.name == "page_route_prefixes"

    assert PageRegistry.__table__.c.code.primary_key is True
    assert PageRegistry.__table__.c.parent_code.nullable is True
    assert PageRegistry.__table__.c.read_permission_id.nullable is True
    assert PageRegistry.__table__.c.write_permission_id.nullable is True
    assert PageRoutePrefix.__table__.c.page_code.nullable is False


def test_erp_navigation_contract_shape() -> None:
    payload = ErpNavigationOut.model_validate(
        {
            "items": [
                {
                    "code": "erp.apps",
                    "name": "应用中心",
                    "parent_code": None,
                    "level": 1,
                    "domain_code": "erp",
                    "show_in_topbar": True,
                    "show_in_sidebar": True,
                    "sort_order": 20,
                    "route_prefixes": ["/apps"],
                    "primary_route": "/apps",
                    "children": [],
                }
            ]
        }
    )

    assert payload.items[0].primary_route == "/apps"


def test_seed_page_codes_are_intentional() -> None:
    assert {
        "erp.portal",
        "erp.apps",
        "erp.cockpit",
        "erp.system",
        "erp.system.users",
    } == {
        "erp.portal",
        "erp.apps",
        "erp.cockpit",
        "erp.system",
        "erp.system.users",
    }
