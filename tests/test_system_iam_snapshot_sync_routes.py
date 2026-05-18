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


def test_system_iam_snapshot_sync_route_is_mounted() -> None:
    assert (
        "POST",
        "/admin/system-iam/apps/{code}/sync-iam-snapshot",
    ) in _method_paths()
