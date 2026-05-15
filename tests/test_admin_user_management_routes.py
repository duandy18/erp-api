from __future__ import annotations

from app.main import app


def _method_paths() -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", None) or []
        for method in methods:
            if method in {"GET", "POST", "PATCH", "PUT", "DELETE"}:
                pairs.add((method, path))
    return pairs


def test_admin_user_management_routes_are_mounted() -> None:
    pairs = _method_paths()

    assert ("GET", "/admin/users/permission-matrix") in pairs
    assert ("GET", "/admin/users") in pairs
    assert ("POST", "/admin/users") in pairs
    assert ("PATCH", "/admin/users/{user_id}") in pairs
    assert ("PUT", "/admin/users/{user_id}/permission-matrix") in pairs
    assert ("POST", "/admin/users/{user_id}/delete") in pairs
    assert ("POST", "/admin/users/{user_id}/reset-password") in pairs
