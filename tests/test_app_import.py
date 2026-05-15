from __future__ import annotations

from fastapi import FastAPI

from app.main import app


def test_app_imports() -> None:
    assert isinstance(app, FastAPI)
