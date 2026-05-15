from __future__ import annotations

from app.core.database import ping_database


def main() -> None:
    ping_database()
    print("ERP database smoke check OK")


if __name__ == "__main__":
    main()
