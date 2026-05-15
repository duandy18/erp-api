from __future__ import annotations

from app.main import app


def main() -> None:
    for route in sorted(app.routes, key=lambda item: getattr(item, "path", "")):
        path = getattr(route, "path", "")
        methods = ",".join(sorted(getattr(route, "methods", []) or []))
        name = getattr(route, "name", "")
        print(f"{methods:20s} {path:30s} {name}")


if __name__ == "__main__":
    main()
