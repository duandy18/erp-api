"""erp_baseline

Revision ID: 0001_erp_baseline
Revises:
Create Date: 2026-05-15 17:30:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

revision: str = "0001_erp_baseline"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create ERP baseline revision."""


def downgrade() -> None:
    """Downgrade ERP baseline revision."""
