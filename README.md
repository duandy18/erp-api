# erp-api

ERP Control Plane API.

ERP 是控制面，不是业务大单体，也不是总数据库。

## Scope

This service will own IAM, App Registry, Gateway metadata, Service Authorization, Workflow tracking, Alerts, Audit, Notifications, Cockpit summary, and Integration adapters.

This service must not directly read or write WMS / PMS / OMS / Procurement / Logistics business databases.

## Local contracts

ERP API: 7990  
ERP DB: 127.0.0.1:5433/erp  
ERP test DB: 127.0.0.1:5433/erp_test  

## Setup

Run from repo root:

    python3 -m venv .venv
    .venv/bin/python3 -m pip install -U pip
    .venv/bin/python3 -m pip install -e ".[dev]"

## Run

    make uvicorn

## Checks

    make lint
    make routes
    make openapi
    make db-smoke
    make upgrade-dev
    make alembic-current
    make alembic-check
    make test
