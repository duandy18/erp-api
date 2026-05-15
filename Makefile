.RECIPEPREFIX := >

PYTHON ?= .venv/bin/python3
PORT ?= 7990
DATABASE_URL ?= postgresql+psycopg://erp:erp@127.0.0.1:5433/erp

export ERP_DATABASE_URL := $(DATABASE_URL)

.PHONY: install lint test routes openapi db-smoke upgrade-dev alembic-current alembic-check uvicorn

install:
> python3 -m venv .venv
> $(PYTHON) -m pip install -U pip
> $(PYTHON) -m pip install -e ".[dev]"

lint:
> $(PYTHON) -m ruff check .

test:
> $(PYTHON) -m pytest

routes:
> $(PYTHON) scripts/print_routes.py

openapi:
> $(PYTHON) scripts/export_openapi.py

db-smoke:
> $(PYTHON) scripts/db_smoke.py

upgrade-dev:
> $(PYTHON) -m alembic upgrade head

alembic-current:
> $(PYTHON) -m alembic current

alembic-check:
> $(PYTHON) -m alembic check

uvicorn:
> ERP_DATABASE_URL="$(ERP_DATABASE_URL)" $(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port $(PORT) --reload
